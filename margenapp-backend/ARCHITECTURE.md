# 🏗️ Arquitectura - Endpoint POST /api/productos/crear

## 📊 Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ANGULAR FRONTEND (localhost:4200)                  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Formulario con validación local (Angular Validators)            │  │
│  │ - nombre: requerido, max 100 chars                              │  │
│  │ - categoria: requerido, max 50 chars                            │  │
│  │ - precio: requerido, min 0.01                                   │  │
│  │ - margen_objetivo: requerido, 0-1                               │  │
│  │ - cantidad_inicial: min 0                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ HttpClient.post('/api/productos/crear', producto)               │  │
│  │ Headers: { 'Content-Type': 'application/json' }                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
└────────────────────────────────────┼─────────────────────────────────────┘
                                     │
                      HTTP POST (JSON payload)
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND (localhost:8000)                       │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ PASO 1: Recibir Request                                         │  │
│  │ @app.post("/api/productos/crear")                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ PASO 2: Validar con Pydantic (ProductoCreate)                   │  │
│  │ - nombre: str, min_length=1, max_length=100 ✅                  │  │
│  │ - categoria: str, min_length=1, max_length=50 ✅                │  │
│  │ - precio: float, gt=0 ✅                                         │  │
│  │ - margen_objetivo: float, ge=0, le=1 ✅                         │  │
│  │ - cantidad_inicial: int, ge=0, default=0 ✅                     │  │
│  │                                                                  │  │
│  │ Si validación falla → Retorna 422 Unprocessable Entity          │  │
│  │ Si validación OK → Continúa                                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ PASO 3: Conectar a PostgreSQL                                   │  │
│  │ conn = psycopg2.connect(**DB_PARAMS)                            │  │
│  │ - localhost:5433                                                │  │
│  │ - DB: margenapp_db                                              │  │
│  │ - User: postgres                                                │  │
│  │                                                                  │  │
│  │ Si conexión falla → Retorna 503 Service Unavailable             │  │
│  │ Si conexión OK → Continúa                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ PASO 4: Guardar en Base de Datos                                │  │
│  │                                                                  │  │
│  │ INSERT INTO productos (                                         │  │
│  │   nombre, categoria, precio, margen_objetivo,                  │  │
│  │   cantidad_inicial, fecha_creacion                             │  │
│  │ ) VALUES (?, ?, ?, ?, ?, NOW())                                │  │
│  │ RETURNING id;                                                   │  │
│  │                                                                  │  │
│  │ Si INSERT falla → Retorna 500 Internal Server Error             │  │
│  │ Si INSERT OK → Obtiene ID único y continúa                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ PASO 5: Ejecutar Algoritmo Predictivo                           │  │
│  │ evaluar_riesgo_con_ia(precio, margen_objetivo)                  │  │
│  │                                                                  │  │
│  │ 1. Calcular variacion_ventas basado en margen:                  │  │
│  │    if margen < 0.05:  variacion_ventas = -0.40 (ALTO RIESGO)    │  │
│  │    elif margen < 0.15: variacion_ventas = -0.15 (RIESGO MEDIO)   │  │
│  │    else:               variacion_ventas = -0.05 (RIESGO BAJO)    │  │
│  │                                                                  │  │
│  │ 2. Preparar datos para modelo:                                  │  │
│  │    X = [[variacion_ventas, margen_objetivo]]                    │  │
│  │                                                                  │  │
│  │ 3. Predicción con Decision Tree Classifier:                     │  │
│  │    prediccion = modelo_ia.predict(X)  → [0, 1 ó 2]              │  │
│  │    probabilidades = modelo_ia.predict_proba(X)                  │  │
│  │                                                                  │  │
│  │ 4. Mapear predicción a texto:                                   │  │
│  │    0 → "BAJO"  | 1 → "MEDIO"  | 2 → "ALTO"                     │  │
│  │                                                                  │  │
│  │ 5. Generar recomendación personalizada                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ PASO 6: Construir Respuesta (ProductoResponse)                  │  │
│  │                                                                  │  │
│  │ {                                                               │  │
│  │   "id": 1,                                                      │  │
│  │   "nombre": "Laptop Dell XPS 13",                               │  │
│  │   "categoria": "Electrónica",                                   │  │
│  │   "precio": 1200.00,                                            │  │
│  │   "margen_objetivo": 0.20,                                      │  │
│  │   "cantidad_inicial": 10,                                       │  │
│  │   "nivel_riesgo": "BAJO",                                       │  │
│  │   "probabilidad_riesgo": 5.2,                                   │  │
│  │   "mensaje": "✅ Riesgo bajo. Margen saludable...",              │  │
│  │   "fecha_creacion": "2026-07-14T14:33:01.965000"                │  │
│  │ }                                                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ PASO 7: Retornar Respuesta                                      │  │
│  │ Status Code: 201 Created                                        │  │
│  │ Headers: { 'Content-Type': 'application/json' }                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
└────────────────────────────────────┼─────────────────────────────────────┘
                                     │
                      HTTP 201 (JSON response)
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      ANGULAR FRONTEND (localhost:4200)                  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Procesar respuesta en subscribe()                               │  │
│  │ - Mostrar datos en tabla                                        │  │
│  │ - Mostrar badge de riesgo (BAJO=verde, MEDIO=amarillo, etc)    │  │
│  │ - Mostrar mensaje de recomendación                              │  │
│  │ - Resetear formulario                                           │  │
│  │ - Mostrar notificación de éxito                                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ UI Actualizada:                                                 │  │
│  │ ✅ Producto guardado en BD                                       │  │
│  │ ✅ Evaluación de riesgo calculada                                │  │
│  │ ✅ Usuario ve el resultado                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Estados y Transiciones

```
START
  │
  ├─→ VALIDACION (Pydantic)
  │     │
  │     ├─→ ❌ FALLA → HTTP 422 Unprocessable Entity → END
  │     │
  │     └─→ ✅ OK → CONEXION BD
  │
  ├─→ CONEXION BD (psycopg2)
  │     │
  │     ├─→ ❌ FALLA → HTTP 503 Service Unavailable → END
  │     │
  │     └─→ ✅ OK → GUARDAR BD
  │
  ├─→ GUARDAR BD (INSERT)
  │     │
  │     ├─→ ❌ FALLA → Rollback + HTTP 500 Internal Error → END
  │     │
  │     └─→ ✅ OK → PREDICCION IA
  │
  ├─→ PREDICCION IA (Scikit-Learn)
  │     │
  │     └─→ ✅ Predicción → RESPUESTA
  │
  ├─→ RESPUESTA (ProductoResponse)
  │     │
  │     └─→ HTTP 201 Created → END (ÉXITO)
  │
  └─→ FINALLY: Cerrar conexión a BD
```

---

## 🔍 Mapeo de Campos

### Request (Angular → Backend)
```
Angular Form
    ↓
HttpClient.post()
    ↓
JSON Body
    ↓
FastAPI recibe
    ↓
ProductoCreate (Pydantic valida)
    ↓
función crear_producto(producto: ProductoCreate)
```

### Response (Backend → Angular)
```
guardar_producto_en_db() → producto_id
evaluar_riesgo_con_ia() → (nivel_riesgo, probabilidad, mensaje)
    ↓
ProductoResponse constructor
    ↓
response_model=ProductoResponse → Serialización JSON
    ↓
HTTP 201 Created
    ↓
Angular recibe response
    ↓
Component.subscribe() → Procesa datos y actualiza UI
```

---

## 🗄️ Base de Datos

### Tabla: productos
```sql
CREATE TABLE productos (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  categoria VARCHAR(50) NOT NULL,
  precio NUMERIC(10, 2) NOT NULL,
  margen_objetivo NUMERIC(5, 4) NOT NULL,
  cantidad_inicial INTEGER DEFAULT 0,
  fecha_creacion TIMESTAMP DEFAULT NOW()
);
```

### Relación con endpoint:
```
INSERT INTO productos (nombre, categoria, precio, margen_objetivo, cantidad_inicial, fecha_creacion)
VALUES (
  @producto.nombre,           ← ProductoCreate.nombre
  @producto.categoria,        ← ProductoCreate.categoria
  @producto.precio,           ← ProductoCreate.precio
  @producto.margen_objetivo,  ← ProductoCreate.margen_objetivo
  @producto.cantidad_inicial, ← ProductoCreate.cantidad_inicial
  NOW()
)
RETURNING id;  ← Retorna en ProductoResponse.id
```

---

## 🤖 Algoritmo de Riesgo (Simplified View)

```
ENTRADA:
  - margen_objetivo (0 a 1)

LÓGICA:
  IF margen < 0.05:
    variacion_ventas = -0.40
    → Probabilidad ALTO = ~83%
  ELIF margen < 0.15:
    variacion_ventas = -0.15
    → Probabilidad MEDIO = ~67%
  ELSE:
    variacion_ventas = -0.05
    → Probabilidad BAJO = ~10%

PREDICTOR (Decision Tree):
  X = [[variacion_ventas, margen_objetivo]]
  prediccion = modelo_ia.predict(X)
  
  IF prediccion == 0:
    nivel_riesgo = "BAJO" ✅
  ELIF prediccion == 1:
    nivel_riesgo = "MEDIO" ⚠️
  ELSE:
    nivel_riesgo = "ALTO" 🔴

SALIDA:
  {
    nivel_riesgo,
    probabilidad_riesgo,
    recomendacion personalizada
  }
```

---

## 🔄 Manejo de Errores

```
┌────────────────────┬──────────────┬────────────────────────────────┐
│ Tipo de Error      │ Status Code  │ Ejemplo                        │
├────────────────────┼──────────────┼────────────────────────────────┤
│ Validación Fallida │ 422          │ Precio negativo                │
│ BD No Disponible   │ 503          │ PostgreSQL no corre            │
│ Error al Guardar   │ 500          │ Tabla no existe                │
│ Otro Error         │ 500          │ Excepción no prevista          │
└────────────────────┴──────────────┴────────────────────────────────┘
```

---

## 🧪 Flujo de Testing

```
test_producto_valido()
  ├─→ POST con datos correctos
  └─→ Assert status != 422

test_nombre_vacio()
  ├─→ POST con nombre = ""
  └─→ Assert status == 422

test_precio_negativo()
  ├─→ POST con precio < 0
  └─→ Assert status == 422

test_nivel_riesgo_valido()
  ├─→ POST con datos válidos
  ├─→ Assert response status == 201
  └─→ Assert nivel_riesgo in ["BAJO", "MEDIO", "ALTO"]

test_margen_alto_riesgo_bajo()
  ├─→ POST con margen = 0.25
  └─→ Assert nivel_riesgo ∈ ["BAJO", "MEDIO"]

test_margen_bajo_riesgo_alto()
  ├─→ POST con margen = 0.03
  └─→ Assert nivel_riesgo ∈ ["ALTO", "MEDIO"]
```

---

## 📊 Matriz de Decisión (Riesgo)

```
┌─────────────────┬──────────────────┬─────────────┬─────────────────┐
│ Margen Objetivo │ Variación Ventas │ Predicción  │ Nivel Riesgo    │
├─────────────────┼──────────────────┼─────────────┼─────────────────┤
│ 0 ≤ m < 0.05    │ -0.40            │ 2           │ 🔴 ALTO         │
│ 0.05 ≤ m < 0.15 │ -0.15            │ 1           │ ⚠️ MEDIO        │
│ 0.15 ≤ m ≤ 1.0  │ -0.05            │ 0           │ ✅ BAJO         │
└─────────────────┴──────────────────┴─────────────┴─────────────────┘
```

---

## 🔌 Integraciones

```
┌──────────────┐
│   Angular    │ ← Frontend
└──────┬───────┘
       │ HTTP/REST
       │
┌──────▼───────┐
│   FastAPI    │ ← Backend (main.py)
├──────────────┤
│ - Pydantic   │ ← Validación
│ - Pandas     │ ← Data Processing
│ - Scikit-Learn│ ← ML/IA
│ - psycopg2   │ ← BD Driver
└──────┬───────┘
       │
┌──────▼───────┐
│ PostgreSQL   │ ← Base de Datos
└──────────────┘
```

---

## ⏱️ Secuencia de Tiempo (Typical)

```
Evento                          Tiempo Aproximado
─────────────────────────────────────────────────
1. Angular envía POST           T+0ms
2. Pydantic valida              T+5ms
3. Conectar a BD                T+10ms
4. INSERT producto              T+20ms
5. Ejecutar predictor IA        T+25ms
6. Construir respuesta          T+28ms
7. Retornar HTTP 201            T+30ms
8. Angular renderiza resultado  T+50ms
─────────────────────────────────────────────────
TOTAL (tiempo percibido):       ~50-100ms
```

---

## 📈 Escalabilidad

### Mejoras futuras:
1. **Caché (Redis)** - Cache de predicciones frecuentes
2. **Async/await** - Operaciones no bloqueantes
3. **Connection Pool** - Reutilizar conexiones BD
4. **Rate Limiting** - Proteger contra abuso
5. **Logging Centralizado** - ELK Stack
6. **Monitoring** - Prometheus + Grafana
7. **CI/CD** - GitHub Actions
8. **Load Balancer** - Nginx/Traefik

