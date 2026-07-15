# 📐 Arquitectura Refactorizada de MargenApp

## 🎯 Objetivo

Transformar el backend de un archivo monolítico (`main.py`) a una arquitectura **modular, escalable y mantenible** siguiendo principios de **Clean Architecture** y **Separation of Concerns**.

---

## 📁 Estructura del Proyecto Backend

```
margenapp-backend/
├── main.py                    # 📌 Punto de entrada (thin - solo 45 líneas)
├── config.py                  # ⚙️ Configuración centralizada
├── schemas.py                 # 📋 Esquemas Pydantic (validación)
├── database.py                # 🗄️ Operaciones CRUD (Repositories)
├── ia_service.py              # 🤖 Servicio de Inteligencia Artificial
├── services.py                # 🔄 Lógica de negocio
├── routes.py                  # 🛣️ Endpoints de la API
├── requirements.txt           # 📦 Dependencias
├── test_main.py               # 🧪 Tests unitarios
└── README.md                  # 📖 Documentación
```

---

## 🏗️ Capas de la Arquitectura

### 1. **Capa de Entrada (main.py)**
**Responsabilidad:** Inicializar la aplicación FastAPI y registrar routers.

```python
# Solo 45 líneas - muy limpio
from fastapi import FastAPI
from routes import router_productos, router_ventas

app = FastAPI(...)
app.include_router(router_productos)
app.include_router(router_ventas)
```

**Ventajas:**
- Fácil de entender qué hace la app
- Menos de 50 líneas de código
- Escalable para agregar más routers

---

### 2. **Capa de Configuración (config.py)**
**Responsabilidad:** Centralizar todas las constantes y variables de entorno.

```python
DB_PARAMS = {
    "dbname": getenv("DB_NAME", "margenapp_db"),
    "user": getenv("DB_USER", "postgres"),
    ...
}

MENSAJES = {
    "producto_creado": "Producto creado exitosamente",
    "venta_registrada": "Venta registrada..."
}
```

**Ventajas:**
- Un único lugar para cambiar configuración
- Fácil gestión de variables de entorno
- Reutilizable en toda la app

---

### 3. **Capa de Validación (schemas.py)**
**Responsabilidad:** Definir esquemas Pydantic para validación automática.

```python
class ProductoCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    precio: float = Field(..., gt=0)
    
    @validator('nombre')
    def nombre_no_vacio(cls, v):
        if not v or v.strip() == "":
            raise ValueError("No puede estar vacío")
        return v.strip()
```

**Ventajas:**
- Validación automática en endpoints
- Documentación automática en Swagger
- Errores 422 descriptivos
- Reutilizable en servicios

---

### 4. **Capa de Base de Datos (database.py) - Repositories Pattern**
**Responsabilidad:** Encapsular todas las operaciones CRUD.

Clases implementadas:
- `DatabaseConnection`: Gestión de conexiones
- `ProductoRepository`: CRUD de productos
- `VentaRepository`: CRUD de ventas
- `AnálisisRepository`: CRUD de análisis

```python
class ProductoRepository:
    @staticmethod
    def crear(conn, nombre, categoria, precio, margen) -> int:
        # Lógica INSERT
        
    @staticmethod
    def obtener_todos(conn) -> List[Dict]:
        # Lógica SELECT
        
    @staticmethod
    def obtener_por_id(conn, id) -> Optional[Dict]:
        # Lógica SELECT WHERE
```

**Ventajas:**
- Acceso centralizado a BD
- Fácil de testear
- Reutilizable desde múltiples servicios
- Un solo lugar para cambiar queries SQL

---

### 5. **Capa de Inteligencia Artificial (ia_service.py)**
**Responsabilidad:** Lógica de predicción y evaluación de riesgo.

```python
class IAService:
    def __init__(self):
        self.modelo = self._entrenar_modelo()
    
    def evaluar_riesgo(self, precio: float, margen: float) -> tuple:
        # Lógica de predicción
        # Retorna: (nivel_riesgo, probabilidad, recomendacion, variacion)
```

**Ventajas:**
- Encapsulación de modelo ML
- Fácil de reemplazar con otro modelo
- Testeable en aislamiento
- Reutilizable desde múltiples servicios

---

### 6. **Capa de Lógica de Negocio (services.py)**
**Responsabilidad:** Orquestar operaciones complejas usando repositories + IA.

Clases implementadas:
- `ProductoService`: Lógica de productos
- `VentaService`: Lógica de ventas

```python
class ProductoService:
    def __init__(self, ia_service: IAService):
        self.ia_service = ia_service
    
    def crear_producto(self, ...):
        # 1. Validar entrada (hecho por schemas.py)
        # 2. Guardar en BD (ProductoRepository)
        # 3. Evaluar riesgo (IAService)
        # 4. Guardar análisis (AnálisisRepository)
        # 5. Retornar respuesta
```

**Ventajas:**
- Lógica de negocio centralizada
- Fácil de testear
- Reutilizable desde múltiples endpoints
- Separado de la BD y de la IA

---

### 7. **Capa de Endpoints (routes.py)**
**Responsabilidad:** Definir rutas y delegar lógica a servicios.

```python
@router_productos.post("/crear", response_model=ProductoResponse)
def crear_producto(producto: ProductoCreate):
    try:
        resultado = producto_service.crear_producto(...)
        return resultado
    except Exception as e:
        raise HTTPException(...)
```

**Ventajas:**
- Endpoints muy limpios y fáciles de leer
- Lógica separada en servicios
- Manejo de errores centralizado
- Documentación automática en Swagger

---

## 🔄 Flujo de una Solicitud

```
1. Cliente (Angular)
   ↓
2. FastAPI recibe petición en routes.py
   ↓
3. Pydantic valida el schema
   ↓
4. Service orquesta la lógica
   ├── Repository accede a BD
   ├── IAService predice riesgo
   └── Repository guarda resultado
   ↓
5. Retorna respuesta al cliente
```

---

## 🧪 Testing

Cada capa es **fácil de testear de forma aislada**:

```python
# Test de Repository
def test_crear_producto():
    repo = ProductoRepository()
    # Mock de conexión
    id = repo.crear(mock_conn, "Laptop", "Electrónica", 1200, 0.2)
    assert id > 0

# Test de IAService
def test_evaluar_riesgo():
    ia = IAService()
    nivel, prob, rec, var = ia.evaluar_riesgo(1200, 0.2)
    assert nivel in ["BAJO", "MEDIO", "ALTO"]

# Test de Service
def test_crear_producto_service():
    ia_service = IAService()
    service = ProductoService(ia_service)
    # Mock de repositories
    resultado = service.crear_producto("Laptop", ...)
    assert resultado["nivel_riesgo"]
```

---

## 📈 Ventajas de esta Arquitectura

| Aspecto | Antes | Después |
|--------|-------|---------|
| **Líneas en main.py** | 442 | 45 |
| **Responsabilidades** | 8 | 1 |
| **Testabilidad** | Difícil (todo acoplado) | Fácil (cada módulo aislado) |
| **Mantenibilidad** | Baja (cambios afectan todo) | Alta (cambios localizados) |
| **Reutilización** | No (lógica duplicada) | Sí (servicios reutilizables) |
| **Escalabilidad** | Baja (agregar features requiere refactorizar) | Alta (agregar features es modular) |

---

## 🚀 Cómo Agregar Nuevas Features

### Ejemplo: Agregar endpoint para obtener reporte de ventas

```python
# 1. En schemas.py - agregar esquema de respuesta
class ReporteVentasResponse(BaseModel):
    periodo: str
    total_ventas: float
    cantidad_productos: int

# 2. En database.py - agregar método a VentaRepository
class VentaRepository:
    @staticmethod
    def obtener_reporte(conn, fecha_inicio, fecha_fin):
        # Query SQL
        ...

# 3. En services.py - agregar método a VentaService
class VentaService:
    def generar_reporte(self, fecha_inicio, fecha_fin):
        conn = DatabaseConnection.obtener_conexion()
        try:
            datos = VentaRepository.obtener_reporte(conn, ...)
            return {"periodo": "...", "total_ventas": datos}
        finally:
            conn.close()

# 4. En routes.py - agregar endpoint
@router_ventas.get("/reporte", response_model=ReporteVentasResponse)
def obtener_reporte(fecha_inicio: str, fecha_fin: str):
    return venta_service.generar_reporte(fecha_inicio, fecha_fin)
```

**Total: 4 cambios pequeños y localizados**

---

## 🎨 Principios Aplicados

### 1. **Single Responsibility Principle (SRP)**
- Cada módulo tiene **una única responsabilidad**
- `database.py`: Solo BD
- `ia_service.py`: Solo IA
- `services.py`: Solo lógica de negocio
- `routes.py`: Solo endpoints

### 2. **Don't Repeat Yourself (DRY)**
- Lógica de negocio centralizada en servicios
- Queries SQL centralizadas en repositories
- Esquemas reutilizables en múltiples endpoints

### 3. **Dependency Injection**
```python
class ProductoService:
    def __init__(self, ia_service: IAService):
        self.ia_service = ia_service  # Inyectado
```

### 4. **Repository Pattern**
- Abstracción de acceso a datos
- Facilita testing y cambio de BD

### 5. **Service Layer Pattern**
- Orquesta operaciones complejas
- Centraliza lógica de negocio
- Facilita reutilización

---

## 📊 Métricas de Calidad

| Métrica | Valor |
|---------|-------|
| **Cohesión** | Alta (cada módulo hace una cosa bien) |
| **Acoplamiento** | Bajo (módulos independientes) |
| **Reusabilidad** | Alta (servicios reutilizables) |
| **Testabilidad** | Alta (cada módulo testeable) |
| **Mantenibilidad** | Alta (código organizado y claro) |

---

## 🔐 Seguridad

**Buenas prácticas aplicadas:**
- ✅ Validación de entrada con Pydantic
- ✅ Manejo de errores centralizado
- ✅ SQL inyection prevenido (parametrized queries)
- ✅ Errores 422 descriptivos sin exponer detalles internos
- ✅ Variables de entorno para credenciales (vía `config.py`)

---

## 📚 Referencias

- **Arquitectura Limpia**: Clean Architecture by Robert C. Martin
- **Patrones**: Repository Pattern, Service Layer Pattern
- **FastAPI**: https://fastapi.tiangolo.com
- **Pydantic**: https://docs.pydantic.dev

---

## ✅ Próximos Pasos

1. **Agregar logging** - Sistema centralizado de logs
2. **Agregar middleware** - Para monitoring y tracing
3. **Agregar cache** - Caché de redis para optimizar BD
4. **Agregar eventos** - Event bus para operaciones asincrónicas
5. **Agregar CI/CD** - Tests automáticos en cada commit

---

## 📞 Soporte

Para preguntas sobre la arquitectura, consulta:
- `config.py` - Configuración
- `schemas.py` - Validación
- `database.py` - Acceso a datos
- `ia_service.py` - Inteligencia Artificial
- `services.py` - Lógica de negocio
- `routes.py` - Endpoints

**Cada módulo está bien documentado con docstrings**
