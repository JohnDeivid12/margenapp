# 📝 Script SQL - Crear Base de Datos MargenApp

## Prerequisitos

- PostgreSQL instalado y corriendo
- Usuario `postgres` con contraseña `123` (o ajustar en `config.py`)
- Puerto PostgreSQL: `5433` (o `5432` por defecto)

---

## Opción 1: Crear TODO desde cero

### Paso 1: Conectar a PostgreSQL

```bash
# En Windows
psql -U postgres

# En Linux/Mac
psql -U postgres
```

### Paso 2: Ejecutar script completo

Copiar y pegar TODO el siguiente script en psql:

```sql
-- ============================================================================
-- CREAR BASE DE DATOS MARGENAPP
-- ============================================================================

DROP DATABASE IF EXISTS margenapp_db;
CREATE DATABASE margenapp_db;

-- Conectar a la nueva BD
\c margenapp_db

-- ============================================================================
-- CREAR TABLA: PRODUCTOS
-- ============================================================================

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    categoria VARCHAR(50) NOT NULL,
    precio NUMERIC(10, 2) NOT NULL CHECK (precio > 0),
    margen_objetivo NUMERIC(3, 2) NOT NULL CHECK (margen_objetivo >= 0 AND margen_objetivo <= 1),
    cantidad_inicial INT DEFAULT 0 CHECK (cantidad_inicial >= 0),
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- Índices para búsqueda rápida
CREATE INDEX idx_productos_nombre ON productos(nombre);
CREATE INDEX idx_productos_categoria ON productos(categoria);

-- ============================================================================
-- CREAR TABLA: VENTAS DIARIAS
-- ============================================================================

CREATE TABLE ventas_diarias (
    id SERIAL PRIMARY KEY,
    producto_id INT NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_aplicado NUMERIC(10, 2) NOT NULL CHECK (precio_aplicado > 0),
    fecha_venta TIMESTAMP DEFAULT NOW()
);

-- Índices para búsqueda y análisis rápido
CREATE INDEX idx_ventas_producto ON ventas_diarias(producto_id);
CREATE INDEX idx_ventas_fecha ON ventas_diarias(fecha_venta);

-- ============================================================================
-- CREAR TABLA: ANÁLISIS DE PRODUCTOS
-- ============================================================================

CREATE TABLE analisis_productos (
    id SERIAL PRIMARY KEY,
    producto_id INT UNIQUE NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    precio_promedio NUMERIC(10, 2),
    variacion_ventas_pct NUMERIC(5, 2),
    margen_actual_pct NUMERIC(3, 2),
    nivel_riesgo VARCHAR(10) CHECK (nivel_riesgo IN ('BAJO', 'MEDIO', 'ALTO')),
    recomendacion TEXT,
    fecha_analisis TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- Índice para búsqueda rápida
CREATE INDEX idx_analisis_riesgo ON analisis_productos(nivel_riesgo);

-- ============================================================================
-- DATOS DE EJEMPLO (Opcional)
-- ============================================================================

-- Insertar algunos productos de ejemplo
INSERT INTO productos (nombre, categoria, precio, margen_objetivo, cantidad_inicial)
VALUES
    ('Laptop Dell XPS 13', 'Electrónica', 1200.00, 0.20, 5),
    ('Mouse Logitech MX Master', 'Periféricos', 99.99, 0.35, 20),
    ('Monitor LG 27"', 'Periféricos', 299.99, 0.25, 8),
    ('Teclado Mecánico Corsair', 'Periféricos', 199.99, 0.30, 12),
    ('Escritorio Gamer NZXT', 'Muebles', 450.00, 0.15, 3);

-- Verificar que se insertaron
SELECT * FROM productos;

-- ============================================================================
-- VERIFICAR ESTRUCTURA
-- ============================================================================

-- Ver todas las tablas
\dt

-- Ver estructura de cada tabla
\d productos
\d ventas_diarias
\d analisis_productos

-- Ver índices
\di
```

---

## Opción 2: Si la BD ya existe (solo agregar tabla de ventas)

### Ejecutar esto en psql:

```sql
-- Conectar a BD existente
\c margenapp_db

-- Crear tabla de ventas si no existe
CREATE TABLE IF NOT EXISTS ventas_diarias (
    id SERIAL PRIMARY KEY,
    producto_id INT NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_aplicado NUMERIC(10, 2) NOT NULL CHECK (precio_aplicado > 0),
    fecha_venta TIMESTAMP DEFAULT NOW()
);

-- Crear índices
CREATE INDEX IF NOT EXISTS idx_ventas_producto ON ventas_diarias(producto_id);
CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas_diarias(fecha_venta);

-- Verificar estructura
\d ventas_diarias
```

---

## 🧪 Pruebas de la BD

### Verificar conexión desde Python

```python
import psycopg2

try:
    conn = psycopg2.connect(
        dbname="margenapp_db",
        user="postgres",
        password="123",
        host="localhost",
        port="5433"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    print(f"✅ Conexión exitosa. Productos: {len(productos)}")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
```

### Verificar tablas en psql

```sql
-- Ver todas las tablas
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Contar registros por tabla
SELECT 'productos' as tabla, COUNT(*) as registros FROM productos
UNION ALL
SELECT 'ventas_diarias', COUNT(*) FROM ventas_diarias
UNION ALL
SELECT 'analisis_productos', COUNT(*) FROM analisis_productos;
```

---

## 📊 Consultas Útiles

### 1. Ver todos los productos

```sql
SELECT * FROM productos ORDER BY id;
```

### 2. Ver todas las ventas

```sql
SELECT v.*, p.nombre as producto_nombre
FROM ventas_diarias v
LEFT JOIN productos p ON v.producto_id = p.id
ORDER BY v.fecha_venta DESC;
```

### 3. Ver ventas por producto

```sql
SELECT 
    p.nombre,
    p.categoria,
    COUNT(v.id) as total_ventas,
    SUM(v.cantidad) as cantidad_total,
    SUM(v.cantidad * v.precio_aplicado) as ingresos_totales,
    AVG(v.precio_aplicado) as precio_promedio
FROM productos p
LEFT JOIN ventas_diarias v ON p.id = v.producto_id
GROUP BY p.id, p.nombre, p.categoria
ORDER BY ingresos_totales DESC;
```

### 4. Ver análisis de productos

```sql
SELECT 
    p.nombre,
    ap.nivel_riesgo,
    ap.precio_promedio,
    ap.margen_actual_pct,
    ap.variacion_ventas_pct,
    ap.recomendacion
FROM productos p
LEFT JOIN analisis_productos ap ON p.id = ap.producto_id
ORDER BY ap.nivel_riesgo;
```

### 5. Ver productos con riesgo ALTO

```sql
SELECT p.nombre, ap.nivel_riesgo, ap.recomendacion
FROM productos p
LEFT JOIN analisis_productos ap ON p.id = ap.producto_id
WHERE ap.nivel_riesgo = 'ALTO';
```

---

## 🔧 Mantenimiento

### Hacer backup

```bash
pg_dump -U postgres -d margenapp_db > backup_margenapp.sql
```

### Restaurar desde backup

```bash
psql -U postgres -d margenapp_db < backup_margenapp.sql
```

### Limpiar datos de prueba

```sql
-- Eliminar todas las ventas
DELETE FROM ventas_diarias;

-- Eliminar todos los productos (esto también elimina ventas por CASCADE)
DELETE FROM productos;

-- Resetear secuencias de ID
ALTER SEQUENCE productos_id_seq RESTART WITH 1;
ALTER SEQUENCE ventas_diarias_id_seq RESTART WITH 1;
ALTER SEQUENCE analisis_productos_id_seq RESTART WITH 1;
```

---

## ✅ Checklist

- [ ] PostgreSQL está corriendo en localhost:5433
- [ ] Se creó la BD `margenapp_db`
- [ ] Tabla `productos` creada
- [ ] Tabla `ventas_diarias` creada
- [ ] Tabla `analisis_productos` creada
- [ ] Se insertaron datos de ejemplo
- [ ] Se puede conectar desde Python
- [ ] Backend `python main.py` inicia sin errores

---

## 🆘 Troubleshooting

### Error: "psql: FATAL: Ident authentication failed"

**Solución:** Editar `pg_hba.conf`:
```bash
# Cambiar "ident" por "password" para conexión local
local   all             all                                     password
```

### Error: "connection refused port 5433"

**Verificar puerto:**
```bash
# El puerto por defecto es 5432, cambiar en config.py:
psql -p 5432 -U postgres
```

### Error: "password authentication failed"

**Verificar credenciales en config.py:**
```python
DB_PARAMS = {
    "dbname": "margenapp_db",
    "user": "postgres",
    "password": "123",  # ← Asegúrate que es correcto
    "host": "localhost",
    "port": "5433"
}
```

---

## 📚 Recursos

- PostgreSQL: https://www.postgresql.org/download/
- psycopg2: https://www.psycopg.org/
- SQL Tutorial: https://www.w3schools.com/sql/

---

**¡Listo! Tu BD está lista para MargenApp.** 🚀
