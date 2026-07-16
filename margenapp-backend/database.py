"""
Base de datos - Conexión y operaciones CRUD
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException, status
from config import DB_PARAMS
from typing import List, Dict, Optional


class DatabaseConnection:
    """Gestor de conexión a la base de datos PostgreSQL"""
    
    @staticmethod
    def obtener_conexion():
        """Crea una conexión con la base de datos PostgreSQL"""
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            return conn
        except psycopg2.Error as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error de conexión a base de datos: {str(e)}"
            )


class _ProductoRepositoryDuplicado:
    """Operaciones CRUD para productos"""
    
    @staticmethod
    def crear(conn, nombre: str, categoria: str, precio: float, margen_objetivo: float) -> int:
        """Crea un nuevo producto y retorna su ID"""
        try:
            cursor = conn.cursor()
            
            query = """
                INSERT INTO productos (nombre, categoria, precio, margen_objetivo)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """
            
            cursor.execute(query, (nombre, categoria, precio, margen_objetivo))
            producto_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            
            return producto_id
        
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar el producto: {str(e)}"
            )
    
    @staticmethod
    def obtener_todos(conn) -> List[Dict]:
        """Obtiene todos los productos"""
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = "SELECT id, nombre, categoria, precio, margen_objetivo FROM productos ORDER BY id"
            cursor.execute(query)
            productos = cursor.fetchall()
            cursor.close()
            return productos if productos else []
        except psycopg2.Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener productos: {str(e)}"
            )
    
    @staticmethod
    def obtener_por_id(conn, producto_id: int) -> Optional[Dict]:
        """Obtiene un producto específico por ID"""
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM productos WHERE id = %s"
            cursor.execute(query, (producto_id,))
            producto = cursor.fetchone()
            cursor.close()
            return producto
        except psycopg2.Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener producto: {str(e)}"
            )
    
    @staticmethod
    def obtener_precio_y_margen(conn, producto_id: int) -> tuple:
        """Obtiene el precio y margen objetivo de un producto"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT precio, margen_objetivo FROM productos WHERE id = %s", (producto_id,))
            resultado = cursor.fetchone()
            cursor.close()
            
            if not resultado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto con ID {producto_id} no existe"
                )
            
            return resultado
        except psycopg2.Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener producto: {str(e)}"
            )

    # =========================================================================
    # ACTUALIZAR PRODUCTO (Y RECALCULAR ANÁLISIS)
    # =========================================================================
    @staticmethod
    def actualizar(conn, producto_id: int, nombre: str, categoria: str, precio: float, margen_objetivo: float):
        """Actualiza un producto y recalcula su análisis financiero en caliente"""
        try:
            cursor = conn.cursor()
            query = """
                UPDATE productos
                SET nombre = %s, categoria = %s, precio = %s, margen_objetivo = %s
                WHERE id = %s;
            """
            cursor.execute(query, (nombre, categoria, precio, margen_objetivo, producto_id))
            conn.commit()
            cursor.close()

            # Recalcular métricas simples con ventas existentes
            total_unidades, ingresos_totales = VentaRepository.obtener_metricas_por_producto(conn, producto_id)
            costo_implicito = float(precio) * (1.0 - float(margen_objetivo))

            if total_unidades > 0:
                precio_promedio = float(ingresos_totales) / float(total_unidades)
                margen_real = (precio_promedio - costo_implicito) / precio_promedio if precio_promedio > 0 else float(margen_objetivo)
            else:
                precio_promedio = float(precio)
                margen_real = float(margen_objetivo)

            if margen_real >= float(margen_objetivo):
                nivel_riesgo = "BAJO"
                recomendacion = "✅ Riesgo bajo. Margen saludable y ventas estables. Mantener estrategia de precios."
            elif margen_real >= 0.05:
                nivel_riesgo = "MEDIO"
                recomendacion = "⚠️ Riesgo moderado por desviación de margen. Evaluar costos y limitar descuentos adicionales."
            else:
                nivel_riesgo = "ALTO"
                recomendacion = "🚨 Riesgo alto. Rentabilidad crítica. Se recomienda ajustar margen o renegociar costos con proveedores."

            AnálisisRepository.guardar_o_actualizar(
                conn,
                producto_id=producto_id,
                precio_promedio=float(precio_promedio),
                variacion=0.0,
                margen=float(margen_real),
                riesgo=nivel_riesgo,
                recomendacion=recomendacion,
            )

        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar el producto: {str(e)}"
            )

    # =========================================================================
    # ELIMINAR PRODUCTO
    # =========================================================================
    @staticmethod
    def eliminar(conn, producto_id: int):
        """Elimina físicamente un producto por su ID"""
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE id = %s;", (producto_id,))
            conn.commit()
            cursor.close()
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar el producto (Verifique claves foráneas): {str(e)}"
            )


class VentaRepository:
    """Operaciones CRUD para ventas"""
    
    @staticmethod
    def crear(conn, producto_id: int, cantidad: int, precio_aplicado: float) -> int:
        """Crea una nueva venta y retorna su ID"""
        try:
            cursor = conn.cursor()
            
            query = """
                INSERT INTO ventas_diarias (producto_id, cantidad, precio_aplicado, fecha_venta)
                VALUES (%s, %s, %s, NOW())
                RETURNING id;
            """
            
            cursor.execute(query, (producto_id, cantidad, precio_aplicado))
            venta_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            
            return venta_id
        
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar la venta: {str(e)}"
            )
    
    @staticmethod
    def obtener_todos(conn) -> List[Dict]:
        """Obtiene todas las ventas"""
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT vd.id, vd.producto_id, vd.cantidad, vd.precio_aplicado, vd.fecha_venta,
                       p.nombre as producto_nombre
                FROM ventas_diarias vd
                LEFT JOIN productos p ON vd.producto_id = p.id
                ORDER BY vd.fecha_venta DESC
            """
            cursor.execute(query)
            ventas = cursor.fetchall()
            cursor.close()
            return ventas if ventas else []
        except psycopg2.Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener ventas: {str(e)}"
            )
    
    @staticmethod
    def obtener_por_producto(conn, producto_id: int) -> List[Dict]:
        """Obtiene las ventas de un producto específico"""
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT id, producto_id, cantidad, precio_aplicado, fecha_venta
                FROM ventas_diarias
                WHERE producto_id = %s
                ORDER BY fecha_venta DESC
            """
            cursor.execute(query, (producto_id,))
            ventas = cursor.fetchall()
            cursor.close()
            return ventas if ventas else []
        except psycopg2.Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener ventas del producto: {str(e)}"
            )
    
    @staticmethod
    def obtener_metricas_por_producto(conn, producto_id: int) -> tuple:
        """Calcula métricas agregadas de ventas: total unidades e ingresos totales"""
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    COALESCE(SUM(cantidad), 0) as total_unidades,
                    COALESCE(SUM(cantidad * precio_aplicado), 0) as ingresos_totales
                FROM ventas_diarias
                WHERE producto_id = %s;
            """
            cursor.execute(query, (producto_id,))
            total_unidades, ingresos_totales = cursor.fetchone()
            cursor.close()
            
            return int(total_unidades), float(ingresos_totales)
        except psycopg2.Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al calcular métricas: {str(e)}"
            )


class AnálisisRepository:
    """Operaciones CRUD para análisis de productos"""
    
    @staticmethod
    def guardar_o_actualizar(conn, producto_id: int, precio_promedio: float, 
                            variacion: float, margen: float, riesgo: str, recomendacion: str):
        """Inserta o actualiza (Upsert) el análisis de un producto"""
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO analisis_productos (
                    producto_id, precio_promedio, variacion_ventas_pct, margen_actual_pct, 
                    nivel_riesgo, recomendacion, fecha_analisis
                )
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (producto_id) 
                DO UPDATE SET 
                    precio_promedio = EXCLUDED.precio_promedio,
                    variacion_ventas_pct = EXCLUDED.variacion_ventas_pct,
                    margen_actual_pct = EXCLUDED.margen_actual_pct,
                    nivel_riesgo = EXCLUDED.nivel_riesgo,
                    recomendacion = EXCLUDED.recomendacion,
                    fecha_analisis = NOW();
            """
            cursor.execute(query, (producto_id, precio_promedio, variacion, margen, riesgo, recomendacion))
            conn.commit()
            cursor.close()
        except psycopg2.Error as e:
            conn.rollback()
            print(f"⚠️ Error no crítico al guardar análisis: {str(e)}")
    
    @staticmethod
    def obtener_por_producto(conn, producto_id: int) -> Optional[Dict]:
        """Obtiene el análisis de un producto"""
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM analisis_productos WHERE producto_id = %s"
            cursor.execute(query, (producto_id,))
            analisis = cursor.fetchone()
            cursor.close()
            return analisis
        except psycopg2.Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener análisis: {str(e)}"
            )
    
    @staticmethod
    def obtener_todos_con_productos(conn) -> List[Dict]:
        """Obtiene todos los productos con su análisis (LEFT JOIN)"""
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT 
                    p.id, 
                    p.nombre, 
                    p.categoria,
                    p.precio,
                    p.margen_objetivo,
                    COALESCE(a.precio_promedio, 0) AS precio_promedio,
                    COALESCE(a.margen_actual_pct, p.margen_objetivo) AS margen_actual_pct,
                    COALESCE(a.variacion_ventas_pct, 0) AS variacion_ventas_pct,
                    COALESCE(a.nivel_riesgo, 'BAJO') AS nivel_riesgo,
                    COALESCE(a.recomendacion, 'Sin análisis disponible.') AS recomendacion
                FROM productos p
                LEFT JOIN analisis_productos a ON p.id = a.producto_id
                ORDER BY p.id
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            cursor.close()
            return resultados if resultados else []
        except psycopg2.Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener análisis: {str(e)}"
            )
            
class ProductoRepository:
    """Operaciones CRUD para productos"""
    
    @staticmethod
    def crear(conn, nombre: str, categoria: str, precio: float, margen_objetivo: float) -> int:
        # ... (tu código original, no lo toques)
        pass

    @staticmethod
    def obtener_todos(conn) -> List[Dict]:
        # ... (tu código original, no lo toques)
        pass

    @staticmethod
    def obtener_por_id(conn, producto_id: int) -> Optional[Dict]:
        # ... (tu código original, no lo toques)
        pass

    @staticmethod
    def obtener_precio_y_margen(conn, producto_id: int) -> tuple:
        # ... (tu código original, no lo toques)
        pass

    # =========================================================================
    # ACTUALIZAR PRODUCTO (Y RECALCULAR INTEGRACIÓN CON IA)
    # =========================================================================
    @staticmethod
    def actualizar(conn, producto_id: int, nombre: str, categoria: str, precio: float, margen_objetivo: float):
        """Actualiza los datos base de un producto y recalcula de inmediato su análisis financiero"""
        try:
            cursor = conn.cursor()
            query = """
                UPDATE productos 
                SET nombre = %s, categoria = %s, precio = %s, margen_objetivo = %s
                WHERE id = %s;
            """
            cursor.execute(query, (nombre, categoria, precio, margen_objetivo, producto_id))
            conn.commit()
            cursor.close()

            # --- RECALCULO EN CALIENTE TRAS LA EDICIÓN ---
            total_unidades, ingresos_totales = VentaRepository.obtener_metricas_por_producto(conn, producto_id)
            costo_implicito = precio * (1.0 - margen_objetivo)

            if total_unidades > 0:
                precio_promedio = ingresos_totales / total_unidades
                margen_real = (precio_promedio - costo_implicito) / precio_promedio
            else:
                precio_promedio = precio
                margen_real = margen_objetivo

            if margen_real >= margen_objetivo:
                nivel_riesgo = "BAJO"
                recomendacion = "✅ Riesgo bajo. Margen saludable y ventas estables. Mantener estrategia de precios."
            elif margen_real < margen_objetivo and margen_real >= 0.05:
                nivel_riesgo = "MEDIO"
                recomendacion = "⚠️ Riesgo moderado por desviación de margen. Evaluar costos de adquisición y limitar descuentos adicionales."
            else:
                nivel_riesgo = "ALTO"
                recomendacion = "🚨 Riesgo alto. Rentabilidad crítica por debajo del umbral óptimo. Se recomienda subir margen objetivo o renegociar costos con proveedores de inmediato."

            AnálisisRepository.guardar_o_actualizar(
                conn, 
                producto_id=producto_id,
                precio_promedio=precio_promedio,
                variacion=0.0,
                margen=margen_real,
                riesgo=nivel_riesgo,
                recomendacion=recomendacion
            )

        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar el producto: {str(e)}"
            )

    # =========================================================================
    # ELIMINAR PRODUCTO
    # =========================================================================
    @staticmethod
    def eliminar(conn, producto_id: int):
        """Elimina físicamente un producto por su ID de la base de datos"""
        try:
            cursor = conn.cursor()
            query = "DELETE FROM productos WHERE id = %s;"
            cursor.execute(query, (producto_id,))
            conn.commit()
            cursor.close()
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar el producto (Verifique claves foráneas): {str(e)}"
            )

