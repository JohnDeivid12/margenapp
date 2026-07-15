"""
Servicios de negocio - Lógica de aplicación
"""
from database import ProductoRepository, VentaRepository, AnálisisRepository, DatabaseConnection
from ia_service import IAService
from datetime import datetime
from typing import Dict, List


class ProductoService:
    """Servicio de negocio para productos"""
    
    def __init__(self, ia_service: IAService):
        self.ia_service = ia_service
    
    def crear_producto(self, nombre: str, categoria: str, precio: float, 
                      margen_objetivo: float, cantidad_inicial: int = 0) -> Dict:
        """Crea un nuevo producto y realiza análisis inicial de riesgo"""
        conn = DatabaseConnection.obtener_conexion()
        
        try:
            # 1. Guardar producto
            producto_id = ProductoRepository.crear(
                conn, nombre, categoria, precio, margen_objetivo
            )
            
            # 2. Evaluar riesgo
            nivel_riesgo, probabilidad, recomendacion, variacion_ventas = \
                self.ia_service.evaluar_riesgo(precio, margen_objetivo)
            
            # 3. Guardar análisis inicial
            AnálisisRepository.guardar_o_actualizar(
                conn=conn,
                producto_id=producto_id,
                precio_promedio=precio,
                variacion=variacion_ventas,
                margen=margen_objetivo,
                riesgo=nivel_riesgo,
                recomendacion=recomendacion
            )
            
            return {
                "id": producto_id,
                "nombre": nombre,
                "categoria": categoria,
                "precio": precio,
                "margen_objetivo": margen_objetivo,
                "nivel_riesgo": nivel_riesgo,
                "probabilidad_riesgo": probabilidad,
                "mensaje": recomendacion,
                "fecha_creacion": datetime.now().isoformat()
            }
        
        finally:
            conn.close()
    
    def obtener_todos_con_analisis(self) -> List[Dict]:
        """Obtiene todos los productos con su análisis"""
        conn = DatabaseConnection.obtener_conexion()
        
        try:
            resultados = AnálisisRepository.obtener_todos_con_productos(conn)
            
            productos_respuesta = []
            for row in resultados:
                # Recalcular probabilidad de riesgo
                nivel_riesgo, probabilidad, recomendacion, _ = \
                    self.ia_service.evaluar_riesgo(
                        float(row['precio_promedio']),
                        float(row['margen_actual_pct'])
                    )
                
                productos_respuesta.append({
                    "id": int(row['id']),
                    "nombre": row['nombre'],
                    "categoria": row['categoria'],
                    "precio": float(row['precio']),
                    "precio_promedio": float(row['precio_promedio']),
                    "margen_objetivo": float(row['margen_objetivo']),
                    "margen_actual_pct": float(row['margen_actual_pct']),
                    "variacion_ventas_pct": float(row['variacion_ventas_pct']),
                    "nivel_riesgo": row['nivel_riesgo'] or nivel_riesgo,
                    "probabilidad_riesgo": probabilidad,
                    "recomendacion": row['recomendacion'] or recomendacion,
                })
            
            return productos_respuesta
        
        finally:
            conn.close()


class VentaService:
    """Servicio de negocio para ventas"""
    
    def __init__(self, ia_service: IAService):
        self.ia_service = ia_service
    
    def registrar_venta(self, producto_id: int, cantidad: int, precio_aplicado: float) -> Dict:
        """Registra una venta y actualiza el análisis del producto"""
        conn = DatabaseConnection.obtener_conexion()
        
        try:
            # 1. Validar que el producto existe
            precio_original, margen_objetivo = ProductoRepository.obtener_precio_y_margen(conn, producto_id)
            
            # 2. Registrar la venta
            venta_id = VentaRepository.crear(conn, producto_id, cantidad, precio_aplicado)
            
            # 3. Calcular nuevas métricas
            total_unidades, ingresos_totales = VentaRepository.obtener_metricas_por_producto(conn, producto_id)
            
            # Nuevo precio promedio
            if total_unidades > 0:
                precio_promedio = float(ingresos_totales) / total_unidades
            else:
                precio_promedio = float(precio_original)
            
            # Estimar margen real
            costo_implicito = float(precio_original) * (1 - float(margen_objetivo))
            if precio_promedio > 0:
                margen_real = (precio_promedio - costo_implicito) / precio_promedio
            else:
                margen_real = float(margen_objetivo)
            
            # 4. Reevaluar riesgo
            nivel_riesgo, probabilidad, recomendacion, variacion_ventas = \
                self.ia_service.evaluar_riesgo(precio_promedio, margen_real)
            
            # 5. Actualizar análisis
            AnálisisRepository.guardar_o_actualizar(
                conn=conn,
                producto_id=producto_id,
                precio_promedio=precio_promedio,
                variacion=variacion_ventas,
                margen=margen_real,
                riesgo=nivel_riesgo,
                recomendacion=recomendacion
            )
            
            # Obtener la venta registrada
            fecha_venta = datetime.now().isoformat()
            
            return {
                "id": venta_id,
                "producto_id": producto_id,
                "cantidad": cantidad,
                "precio_aplicado": precio_aplicado,
                "fecha_venta": fecha_venta,
                "nivel_riesgo_actualizado": nivel_riesgo,
                "probabilidad_riesgo_actualizado": probabilidad,
                "mensaje": recomendacion
            }
        
        finally:
            conn.close()
    
    def obtener_todas_las_ventas(self) -> List[Dict]:
        """Obtiene todas las ventas registradas"""
        conn = DatabaseConnection.obtener_conexion()
        
        try:
            ventas = VentaRepository.obtener_todos(conn)
            
            return [
                {
                    "id": int(v['id']),
                    "producto_id": int(v['producto_id']),
                    "producto_nombre": v.get('producto_nombre', 'N/A'),
                    "cantidad": int(v['cantidad']),
                    "precio_aplicado": float(v['precio_aplicado']),
                    "fecha_venta": str(v['fecha_venta'])
                }
                for v in ventas
            ]
        
        finally:
            conn.close()
    
    def obtener_ventas_por_producto(self, producto_id: int) -> List[Dict]:
        """Obtiene las ventas de un producto específico"""
        conn = DatabaseConnection.obtener_conexion()
        
        try:
            ventas = VentaRepository.obtener_por_producto(conn, producto_id)
            
            return [
                {
                    "id": int(v['id']),
                    "producto_id": int(v['producto_id']),
                    "cantidad": int(v['cantidad']),
                    "precio_aplicado": float(v['precio_aplicado']),
                    "fecha_venta": str(v['fecha_venta'])
                }
                for v in ventas
            ]
        
        finally:
            conn.close()
