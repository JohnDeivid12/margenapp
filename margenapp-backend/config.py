"""
Configuración central de la aplicación MargenApp
"""
from os import getenv

# Configuración de la base de datos PostgreSQL
DB_PARAMS = {
    "dbname": getenv("DB_NAME", "margenapp_db"),
    "user": getenv("DB_USER", "postgres"),
    "password": getenv("DB_PASSWORD", "123"),
    "host": getenv("DB_HOST", "localhost"),
    "port": getenv("DB_PORT", "5433")
}

# Configuración de CORS
CORS_ORIGINS = getenv("CORS_ORIGINS", "*").split(",")

# Configuración de la aplicación
APP_TITLE = "MargenApp - AI Backend"
APP_VERSION = "1.0.0"

# Mensajes de respuesta
MENSAJES = {
    "producto_creado": "Producto creado exitosamente",
    "venta_registrada": "Venta registrada con éxito y análisis del producto actualizado",
    "error_db": "Error de conexión a base de datos",
    "error_servidor": "Error interno del servidor",
    "no_productos": "No hay productos registrados",
    "no_ventas": "No hay ventas registradas"
}
