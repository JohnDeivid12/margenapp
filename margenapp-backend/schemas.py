"""
Esquemas Pydantic para validación automática de datos
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class ProductoCreate(BaseModel):
    """Esquema para validar datos del formulario de Angular al crear un producto"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del producto")
    categoria: str = Field(..., min_length=1, max_length=50, description="Categoría del producto")
    precio: float = Field(..., gt=0, description="Precio unitario (debe ser positivo)")
    margen_objetivo: float = Field(..., ge=0, le=1, description="Margen objetivo (0-1, ej: 0.25 = 25%)")
    
    @validator('nombre')
    def nombre_no_vacio(cls, v):
        if not v or v.strip() == "":
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()
    
    @validator('categoria')
    def categoria_no_vacia(cls, v):
        if not v or v.strip() == "":
            raise ValueError("La categoría no puede estar vacía")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "nombre": "Laptop Dell XPS 13",
                "categoria": "Electrónica",
                "precio": 1200.00,
                "margen_objetivo": 0.20,
            }
        }


class ProductoResponse(BaseModel):
    """Esquema de respuesta después de guardar el producto"""
    id: int
    nombre: str
    categoria: str
    precio: float
    margen_objetivo: float
    nivel_riesgo: str  # BAJO, MEDIO, ALTO
    probabilidad_riesgo: float  # Porcentaje (0-100)
    mensaje: str  # Recomendación para el usuario
    fecha_creacion: str


class EvaluacionRiesgo(BaseModel):
    """Esquema de respuesta para análisis de riesgo"""
    nivel_riesgo: str
    probabilidad_riesgo: float
    recomendacion: str


class VentaCreate(BaseModel):
    """Esquema para registrar una nueva venta"""
    producto_id: int = Field(..., gt=0, description="ID del producto existente")
    cantidad: int = Field(..., gt=0, description="Cantidad vendida")
    precio_aplicado: float = Field(..., gt=0, description="Precio unitario aplicado")
    
    class Config:
        schema_extra = {
            "example": {
                "producto_id": 1,
                "cantidad": 5,
                "precio_aplicado": 1150.00
            }
        }


class VentaResponse(BaseModel):
    """Esquema de respuesta después de registrar una venta"""
    id: int
    producto_id: int
    cantidad: int
    precio_aplicado: float
    fecha_venta: str
    nivel_riesgo_actualizado: str
    probabilidad_riesgo_actualizado: float
    mensaje: str


class ListaProductosResponse(BaseModel):
    """Para endpoint GET que lista productos"""
    id: int
    nombre: str
    categoria: str
    precio: float
    margen_objetivo: float

class AnálisisProductoResponse(BaseModel):
    """Respuesta completa con análisis de un producto"""
    id: int
    nombre: str
    categoria: str
    precio_promedio: float
    margen_objetivo: float
    margen_actual_pct: float
    variacion_ventas_pct: float
    nivel_riesgo: str
    probabilidad_riesgo: float
    recomendacion: str

class ProductoUpdate(BaseModel):
    nombre: str = Field(..., max_length=150)
    categoria: str = Field(..., max_length=100)
    precio: float = Field(..., gt=0)
    margen_objetivo: float = Field(..., ge=0, le=1)  # Entre 0.0 y 1.0 (ej: 0.20 para 20%)