# ⚡ QUICK START - 5 Minutos para Empezar

## 1️⃣ Instalar Dependencias (1 minuto)

```bash
cd margenapp-backend
pip install -r requirements.txt
```

## 2️⃣ Configurar Base de Datos (2 minutos)

Abrir PostgreSQL y ejecutar:

```sql
CREATE DATABASE margenapp_db;
\c margenapp_db;

CREATE TABLE productos (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  categoria VARCHAR(50) NOT NULL,
  precio NUMERIC(10, 2) NOT NULL,
  margen_objetivo NUMERIC(5, 4) NOT NULL,
  cantidad_inicial INTEGER DEFAULT 0,
  fecha_creacion TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ventas_diarias (
  id SERIAL PRIMARY KEY,
  producto_id INTEGER NOT NULL REFERENCES productos(id),
  cantidad INTEGER NOT NULL,
  precio_aplicado NUMERIC(10, 2) NOT NULL,
  fecha_venta TIMESTAMP DEFAULT NOW()
);
```

## 3️⃣ Iniciar Servidor (1 minuto)

```bash
python main.py
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

## 4️⃣ Probar Endpoint (1 minuto)

Opción A: Con cURL
```bash
curl -X POST http://localhost:8000/api/productos/crear \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop Dell",
    "categoria": "Electrónica",
    "precio": 1200,
    "margen_objetivo": 0.20
  }'
```

Opción B: Ver Swagger UI
```
Abrir en navegador: http://localhost:8000/docs
→ Probar desde la interfaz gráfica
```

## 5️⃣ Ver Resultado

```json
{
  "id": 1,
  "nombre": "Laptop Dell",
  "categoria": "Electrónica",
  "precio": 1200.0,
  "margen_objetivo": 0.2,
  "cantidad_inicial": 0,
  "nivel_riesgo": "BAJO",
  "probabilidad_riesgo": 5.2,
  "mensaje": "✅ Riesgo bajo. Margen saludable del 20.0%. Continúa monitoreando.",
  "fecha_creacion": "2026-07-14T14:33:01.965000"
}
```

---

## 📝 Cambios Comunes

### ❌ Si no funciona la conexión a BD

Edita `main.py` línea 78-84:
```python
DB_PARAMS = {
    "dbname": "margenapp_db",
    "user": "postgres",  # Tu usuario
    "password": "123",   # Tu contraseña
    "host": "localhost",
    "port": "5433"       # Tu puerto
}
```

### ❌ Si obtienes error 422

Verifica que los datos cumplan:
- `nombre`: No vacío, máx 100 caracteres
- `precio`: Mayor a 0
- `margen_objetivo`: Entre 0 y 1

### ❌ Si obtiene error 503

PostgreSQL no está corriendo. Inicia el servicio:
```bash
# Windows
psql -U postgres

# Linux
sudo systemctl start postgresql
```

---

## 🧪 Ejecutar Tests

```bash
pytest test_main.py -v
```

Deberías ver algo como:
```
test_main.py::TestValidacionProductoCreate::test_producto_valido PASSED
test_main.py::TestValidacionProductoCreate::test_nombre_vacio PASSED
...
====== 18 passed in 0.45s ======
```

---

## 📊 Verificar Datos en BD

```bash
# Conectar a BD
psql -U postgres -h localhost -p 5433 -d margenapp_db

# Ver productos
SELECT * FROM productos;

# Ver ventas
SELECT * FROM ventas_diarias;
```

---

## 🔗 Integrar con Angular

Ver archivo: `ANGULAR_INTEGRATION.md`

Resumen:
1. Copiar `ProductoService` (TypeScript)
2. Copiar `CrearProductoComponent`
3. Importar `HttpClientModule` en `app.module.ts`
4. Usar el componente en template

---

## 📚 Documentación Completa

- **README.md** - Instalación y uso
- **ENDPOINT_DOCUMENTATION.md** - API detallada
- **ARCHITECTURE.md** - Diagramas
- **ANGULAR_INTEGRATION.md** - Integración frontend
- **SUMMARY.md** - Resumen ejecutivo

---

## ✅ Checklist

- [ ] Dependencias instaladas (`requirements.txt`)
- [ ] PostgreSQL corriendo en localhost:5433
- [ ] Tablas creadas (`productos`, `ventas_diarias`)
- [ ] Credenciales configuradas en `main.py`
- [ ] Servidor iniciado (`python main.py`)
- [ ] Endpoint funcional (probado con cURL)
- [ ] Tests pasando (`pytest test_main.py`)
- [ ] Documentación revisada

---

## 🎉 ¡Listo!

Tu backend MargenApp está **100% operacional**.

**Siguiente paso:** Integrar con Angular (ver `ANGULAR_INTEGRATION.md`)
