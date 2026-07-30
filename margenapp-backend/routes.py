"""
Rutas (Endpoints) de la API - Separadas por dominio
"""
from fastapi import APIRouter, HTTPException, status
from schemas import ProductoCreate, ProductoResponse, VentaCreate, VentaResponse, AnálisisProductoResponse, ListaProductosResponse
from services import ProductoService, VentaService
from ia_service import IAService
from typing import List, Dict

# Inicializar servicios
ia_service = IAService()
producto_service = ProductoService(ia_service)
venta_service = VentaService(ia_service)

# Crear routers
router_productos = APIRouter(prefix="/api/productos", tags=["Productos"])
router_ventas = APIRouter(prefix="/api/ventas", tags=["Ventas"])
router_salud = APIRouter(tags=["Salud"])


# ============================================================================
# ENDPOINTS DE PRODUCTOS
# ============================================================================

@router_productos.post("/crear", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(producto: ProductoCreate):
    """
    ✨ Crea un nuevo producto y realiza análisis inicial de riesgo
    
    - Valida datos con Pydantic
    - Guarda en PostgreSQL tabla 'productos'
    - Ejecuta algoritmo IA para evaluar riesgo
    - Retorna evaluación completa
    """
    try:
        resultado = producto_service.crear_producto(
            nombre=producto.nombre,
            categoria=producto.categoria,
            precio=producto.precio,
            margen_objetivo=producto.margen_objetivo,
        )
        return resultado
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear producto: {str(e)}"
        )


@router_productos.get("/analisis", response_model=Dict)
def obtener_analisis_riesgo():
    """
    📊 Obtiene todos los productos con análisis de riesgo
    
    - LEFT JOIN con tabla analisis_productos
    - Recalcula probabilidades de riesgo
    - Retorna evaluación completa de cada producto
    """
    try:
        productos = producto_service.obtener_todos_con_analisis()
        return {
            "productos": productos,
            "total": len(productos)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener análisis: {str(e)}"
        )


@router_productos.get("/lista", response_model=Dict)
def listar_productos():
    """
    📋 Obtiene la lista de todos los productos (sin análisis)
    
    Útil para llenar selects/dropdowns en formularios
    """
    try:
        from database import DatabaseConnection, ProductoRepository
        conn = DatabaseConnection.obtener_conexion()
        productos = ProductoRepository.obtener_todos(conn)
        conn.close()
        
        return {
            "productos": [
                {
                    "id": p['id'],
                    "nombre": p['nombre'],
                    "categoria": p['categoria'],
                    "precio": float(p['precio']),
                    "margen_objetivo": float(p['margen_objetivo'])
                }
                for p in productos
            ],
            "total": len(productos)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar productos: {str(e)}"
        )

# ============================================================================
# NUEVO ENDPOINT: EDITAR PRODUCTO (PUT)
# ============================================================================
@router_productos.put("/{producto_id}", status_code=status.HTTP_200_OK)
def editar_producto(producto_id: int, producto_data: ProductoCreate):
    """
    ✏️ Edita los datos de un producto y actualiza en caliente el análisis de riesgo
    """
    try:
        from database import DatabaseConnection, ProductoRepository
        conn = DatabaseConnection.obtener_conexion()
        
        # 1. Verificar si el producto existe
        if not ProductoRepository.obtener_por_id(conn, producto_id):
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Producto no encontrado"
            )
        
        # 2. Actualizar el producto (el repositorio internamente recalcula la IA)
        ProductoRepository.actualizar(
            conn=conn,
            producto_id=producto_id,
            nombre=producto_data.nombre,
            categoria=producto_data.categoria,
            precio=producto_data.precio,
            margen_objetivo=producto_data.margen_objetivo
        )
        conn.close()
        
        return {"message": "Producto actualizado con éxito y métricas recalculadas"}
        
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error al actualizar el producto: {str(e)}"
        )


# ============================================================================
# NUEVO ENDPOINT: ELIMINAR PRODUCTO (DELETE)
# ============================================================================
@router_productos.delete("/{producto_id}", status_code=status.HTTP_200_OK)
def eliminar_producto(producto_id: int):
    """
    🗑️ Elimina permanentemente un producto de la base de datos
    """
    try:
        from database import DatabaseConnection, ProductoRepository
        conn = DatabaseConnection.obtener_conexion()
        
        # 1. Verificar si el producto existe
        if not ProductoRepository.obtener_por_id(conn, producto_id):
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Producto no encontrado"
            )
        
        # 2. Ejecutar la eliminación
        ProductoRepository.eliminar(conn, producto_id)
        conn.close()
        
        return {"message": f"Producto con ID {producto_id} eliminado exitosamente"}
        
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error de integridad o base de datos al eliminar: {str(e)}"
        )

# ============================================================================
# ENDPOINTS DE VENTAS
# ============================================================================

@router_ventas.post("/registrar", response_model=VentaResponse, status_code=status.HTTP_201_CREATED)
def registrar_venta(venta: VentaCreate):
    """
    📝 Registra una nueva venta y actualiza análisis del producto
    
    - Valida que el producto exista
    - Inserta en tabla 'ventas_diarias'
    - Recalcula métricas del producto
    - Reevalúa riesgo con nueva información
    - Actualiza tabla 'analisis_productos'
    """
    try:
        resultado = venta_service.registrar_venta(
            producto_id=venta.producto_id,
            cantidad=venta.cantidad,
            precio_aplicado=venta.precio_aplicado
        )
        return resultado
    except Exception as e:
        print(f"❌ Error al registrar venta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar venta: {str(e)}"
        )


@router_ventas.get("/todas", response_model=Dict)
def obtener_todas_ventas():
    """
    📊 Obtiene todas las ventas registradas
    
    - Incluye información del producto
    - Ordenadas por fecha descendente (más recientes primero)
    """
    try:
        ventas = venta_service.obtener_todas_las_ventas()
        return {
            "ventas": ventas,
            "total": len(ventas)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ventas: {str(e)}"
        )


@router_ventas.get("/producto/{producto_id}", response_model=Dict)
def obtener_ventas_producto(producto_id: int):
    """
    📋 Obtiene las ventas de un producto específico
    
    - Filtrado por producto_id
    - Ordenadas por fecha descendente
    """
    try:
        ventas = venta_service.obtener_ventas_por_producto(producto_id)
        return {
            "producto_id": producto_id,
            "ventas": ventas,
            "total": len(ventas)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ventas: {str(e)}"
        )


# ============================================================================
# ENDPOINTS DE SALUD
# ============================================================================

@router_salud.get("/api/health")
def health_check():
    """🏥 Verifica que el backend está en línea"""
    return {"status": "✅ MargenApp Backend está en línea"}
