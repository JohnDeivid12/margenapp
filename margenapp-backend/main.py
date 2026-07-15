"""
MargenApp - API Backend Principal
Arquitectura modular y escalable
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ORIGINS, APP_TITLE, APP_VERSION
from routes import router_productos, router_ventas, router_salud

# ============================================================================
# INICIALIZACIÓN DE LA APLICACIÓN
# ============================================================================

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Backend de MargenApp con predicción de riesgo basada en IA"
)

# ============================================================================
# CONFIGURACIÓN DE CORS
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: limitar a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REGISTRO DE ROUTERS
# ============================================================================

app.include_router(router_productos)
app.include_router(router_ventas)
app.include_router(router_salud)

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)