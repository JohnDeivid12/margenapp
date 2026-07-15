# 🚀 MargenApp Backend - FastAPI

Backend de la aplicación MargenApp para evaluar el riesgo de productos basado en máquinas de decisión (AI).

---

## 📋 Descripción del Proyecto

Este backend proporciona un **endpoint POST** que:
1. ✅ Recibe datos del formulario de Angular
2. ✅ Valida automáticamente con **Pydantic**
3. ✅ Guarda los datos en **PostgreSQL**
4. ✅ Ejecuta algoritmo predictivo de riesgo
5. ✅ Retorna evaluación en formato JSON

---

## 🛠️ Requisitos Previos

- **Python 3.8+**
- **PostgreSQL 12+** (corriendo en `localhost:5433`)
- **pip** para instalar dependencias

---

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/margenapp.git
cd margenapp/margenapp-backend
```

### 2. Crear entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Crear base de datos (PostgreSQL)

Conectarse a PostgreSQL:
```bash
psql -U postgres -h localhost -p 5433
```

Crear base de datos y tabla:
```sql
-- Crear base de datos
CREATE DATABASE margenapp_db;

-- Conectarse a la base de datos
\c margenapp_db;

-- Crear tabla de productos
CREATE TABLE productos (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  categoria VARCHAR(50) NOT NULL,
  precio NUMERIC(10, 2) NOT NULL,
  margen_objetivo NUMERIC(5, 4) NOT NULL,
  cantidad_inicial INTEGER DEFAULT 0,
  fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- Crear tabla de ventas diarias (opcional, para consultas futuras)
CREATE TABLE ventas_diarias (
  id SERIAL PRIMARY KEY,
  producto_id INTEGER NOT NULL REFERENCES productos(id),
  cantidad INTEGER NOT NULL,
  precio_aplicado NUMERIC(10, 2) NOT NULL,
  fecha_venta TIMESTAMP DEFAULT NOW()
);

-- Crear índices para mejor rendimiento
CREATE INDEX idx_productos_categoria ON productos(categoria);
CREATE INDEX idx_ventas_producto_id ON ventas_diarias(producto_id);
```

### 5. Verificar configuración de BD en `main.py`

Asegúrate que `DB_PARAMS` coincida con tu configuración:
```python
DB_PARAMS = {
    "dbname": "margenapp_db",
    "user": "postgres",
    "password": "tu_contraseña",  # Cambia esto
    "host": "localhost",
    "port": "5433"
}
```

---

## 🚀 Ejecutar el Servidor

```bash
python main.py
```

El servidor estará disponible en:
- **API Base:** `http://localhost:8000`
- **Docs Interactiva (Swagger):** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 📚 API Endpoints

### 🎯 POST /api/productos/crear
**Crear un nuevo producto con evaluación de riesgo**

```bash
curl -X POST http://localhost:8000/api/productos/crear \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop Dell XPS 13",
    "categoria": "Electrónica",
    "precio": 1200.00,
    "margen_objetivo": 0.20,
    "cantidad_inicial": 10
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "nombre": "Laptop Dell XPS 13",
  "categoria": "Electrónica",
  "precio": 1200.00,
  "margen_objetivo": 0.20,
  "cantidad_inicial": 10,
  "nivel_riesgo": "BAJO",
  "probabilidad_riesgo": 5.2,
  "mensaje": "✅ Riesgo bajo. Margen saludable del 20.0%. Continúa monitoreando.",
  "fecha_creacion": "2026-07-14T14:33:01.965000"
}
```

---

### 📊 GET /api/productos/analisis
**Obtener análisis de riesgo de todos los productos**

```bash
curl http://localhost:8000/api/productos/analisis
```

**Response:**
```json
{
  "productos": [
    {
      "id": 1,
      "nombre": "Laptop Dell XPS 13",
      "categoria": "Electrónica",
      "precio": 1200.00,
      "margen_objetivo": 0.20,
      "cantidad_ventas": 5,
      "nivel_riesgo": "BAJO",
      "probabilidad_riesgo": 5.2,
      "recomendacion": "✅ Riesgo bajo..."
    }
  ],
  "total": 1
}
```

---

### ✅ GET /api/health
**Verificar que el servidor está activo**

```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "✅ MargenApp Backend está en línea"
}
```

---

## 🧪 Testing

### Ejecutar tests unitarios
```bash
# Desde la carpeta margenapp-backend
pytest test_main.py -v

# Ver reporte detallado
pytest test_main.py -v --tb=short
```

### Tests incluidos
- ✅ Validaciones de Pydantic (campos requeridos, tipos, rangos)
- ✅ Estructura de respuestas
- ✅ Algoritmo predictivo
- ✅ Manejo de errores
- ✅ Otros endpoints

---

## 📖 Documentación Completa

Ver archivo `ENDPOINT_DOCUMENTATION.md` para:
- Validaciones detalladas
- Ejemplos de integración con Angular (TypeScript)
- Ejemplos de HTML/CSS
- Explicación del algoritmo de riesgo
- Ejemplos con cURL

---

## 🔑 Variables de Entorno (Opcional)

Para mayor seguridad, usa variables de entorno en lugar de hardcoding:

```bash
# .env
DB_NAME=margenapp_db
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5433
```

En `main.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}
```

Instalar `python-dotenv`:
```bash
pip install python-dotenv
```

---

## 🏗️ Estructura del Código

```
margenapp-backend/
├── main.py                        # Archivo principal (FastAPI + endpoints)
├── requirements.txt               # Dependencias Python
├── test_main.py                   # Tests unitarios
├── ENDPOINT_DOCUMENTATION.md      # Documentación detallada
├── README.md                      # Este archivo
└── __pycache__/                   # Cache de Python (ignorar)
```

---

## 📝 Descripción de Funciones

### Esquemas (Pydantic)

```python
ProductoCreate        # Valida datos de entrada (nombre, precio, margen, etc)
ProductoResponse      # Define estructura de respuesta del endpoint POST
EvaluacionRiesgo      # Define estructura de evaluación de riesgo
```

### Funciones Principales

```python
entrenar_modelo_ia()           # Entrena árbol de decisión al iniciar
obtener_conexion_db()          # Crea conexión con PostgreSQL
guardar_producto_en_db()       # Guarda producto validado en BD
evaluar_riesgo_con_ia()        # Ejecuta predicción y retorna riesgo
crear_producto()               # Endpoint POST principal
obtener_analisis_riesgo()      # Endpoint GET para análisis
```

---

## 🤖 Algoritmo de Evaluación de Riesgo

El modelo usa un **Decision Tree Classifier** entrenado con datos sintéticos:

**Variables de entrada:**
- `variacion_ventas_pct`: Variación esperada en ventas (-1 a +1)
- `margen_actual_pct`: Margen objetivo del producto (0 a 1)

**Clasificación:**
- **BAJO (0)**: Margen > 20%, riesgo controlado
- **MEDIO (1)**: Margen 5-20%, requiere atención
- **ALTO (2)**: Margen < 5%, acción inmediata

**Lógica de predicción:**
```python
if margen_objetivo < 0.05:
    variacion_ventas = -0.40  # Alto riesgo
elif margen_objetivo < 0.15:
    variacion_ventas = -0.15  # Riesgo moderado
else:
    variacion_ventas = -0.05  # Riesgo bajo
```

---

## ⚠️ Errores Comunes

### Error: `psycopg2.ProgrammingError: relation "productos" does not exist`
**Solución:** Ejecutar scripts SQL para crear las tablas (ver sección "Crear base de datos")

### Error: `Connection refused` a PostgreSQL
**Solución:** Verificar que PostgreSQL esté ejecutándose en el puerto 5433

### Error: `422 Unprocessable Entity`
**Solución:** Validar que los datos cumplan con los requisitos (precio > 0, margen 0-1, etc)

### Error: `ModuleNotFoundError: No module named 'fastapi'`
**Solución:** Ejecutar `pip install -r requirements.txt`

---

## 🔄 CORS Configuration

El CORS está configurado para aceptar todas las fuentes (para desarrollo):
```python
allow_origins=["*"]
```

**Para producción, cambia esto a:**
```python
allow_origins=["https://tu-dominio.com", "https://www.tu-dominio.com"]
```

---

## 📊 Monitoreo y Logs

El servidor imprime logs en consola:
```
✅ Datos validados: {...}
✅ Producto guardado con ID: 1
✅ Evaluación de riesgo: BAJO (5.2%)
```

Para logs a archivo, configura logging en Python:
```python
import logging

logging.basicConfig(
    filename='margenapp.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

## 🚀 Deployment

### Opción 1: Heroku
```bash
# Crear archivo Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deployar
git push heroku main
```

### Opción 2: Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Opción 3: DigitalOcean / AWS / GCP
Ver documentación oficial de Uvicorn para deployment

---

## 🤝 Contribuciones

1. Haz fork del repositorio
2. Crea una rama para tu feature: `git checkout -b feature/mi-feature`
3. Commit tus cambios: `git commit -am 'Add feature'`
4. Push a la rama: `git push origin feature/mi-feature`
5. Abre un Pull Request

---

## 📄 Licencia

MIT License - Ver archivo LICENSE

---

## 📞 Soporte

- 📧 Email: soporte@margenapp.com
- 💬 Discord: [link a servidor]
- 🐛 Issues: https://github.com/tu-usuario/margenapp/issues

---

## 🎯 Roadmap (Próximas Versiones)

- [ ] Autenticación JWT
- [ ] Endpoint para actualizar productos (PUT)
- [ ] Endpoint para eliminar productos (DELETE)
- [ ] Dashboard de estadísticas
- [ ] Historial de análisis
- [ ] Integración con modelos ML más avanzados
- [ ] API WebSocket para actualizaciones en tiempo real
- [ ] Multiidioma (i18n)

---

**Última actualización:** 14 Julio 2026
**Versión:** 1.0.0-MVP
