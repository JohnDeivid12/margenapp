# 🚀 Guía Rápida - MargenApp Refactorizado

## ⚡ 5 Minutos para Empezar

### Terminal 1: Backend

```bash
cd margenapp-backend

# Primera vez
pip install -r requirements.txt

# Ejecutar
python main.py

# Verificar: http://localhost:8000/docs (Swagger UI)
```

### Terminal 2: Frontend

```bash
cd margenapp-frontend

# Primera vez  
npm install

# Ejecutar
npm start

# Se abre: http://localhost:4200
```

### Terminal 3 (Opcional): Tests

```bash
# Backend tests
cd margenapp-backend
pytest test_main.py -v

# Frontend tests
cd margenapp-frontend
npm test
```

---

## 📋 Estructura Rápida

### Backend
```
main.py              ← Punto de entrada (solo 45 líneas)
├─ config.py         ← Configuración
├─ schemas.py        ← Validación
├─ database.py       ← BD (Repositories)
├─ ia_service.py     ← IA/ML
├─ services.py       ← Lógica negocio
└─ routes.py         ← Endpoints
```

### Frontend
```
dashboard/
├─ dashboard.component.ts      ← Gestor de formularios
├─ dashboard.component.html    ← Vista principal
└─ dashboard.component.css
components/
├─ crear-producto/             ← Formulario de productos
│  ├─ .ts
│  ├─ .html
│  ├─ .css
│  └─ .spec.ts
└─ registrar-venta/            ← Formulario de ventas (NUEVO)
   ├─ .ts
   ├─ .html
   ├─ .css
   └─ .spec.ts
services/
└─ producto.service.ts         ← API HTTP
```

---

## 🔌 Endpoints API

| Método | Endpoint | Propósito |
|--------|----------|-----------|
| **POST** | `/api/productos/crear` | Crear producto |
| **GET** | `/api/productos/analisis` | Análisis de riesgos |
| **GET** | `/api/productos/lista` | Lista productos (dropdown) |
| **POST** | `/api/ventas/registrar` | Registrar venta |
| **GET** | `/api/ventas/todas` | Todas las ventas |
| **GET** | `/api/ventas/producto/{id}` | Ventas por producto |
| **GET** | `/api/health` | Estado del server |

---

## 🧪 Ejemplos de Uso

### 1. Crear Producto

```bash
curl -X POST http://localhost:8000/api/productos/crear \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop Dell",
    "categoria": "Electrónica",
    "precio": 1200.00,
    "margen_objetivo": 0.20
  }'
```

### 2. Registrar Venta

```bash
curl -X POST http://localhost:8000/api/ventas/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "producto_id": 1,
    "cantidad": 5,
    "precio_aplicado": 1150.00
  }'
```

### 3. Obtener Análisis

```bash
curl http://localhost:8000/api/productos/analisis | jq
```

---

## 🎯 Casos de Uso Típicos

### Caso 1: Crear un Producto Nuevo

1. Click "Nuevo Producto"
2. Completar formulario
3. Backend valida, guarda, y ejecuta IA
4. Ver resultado en tarjeta de respuesta
5. Dashboard se actualiza automáticamente

### Caso 2: Registrar una Venta

1. Click "Nueva Venta"
2. Seleccionar producto (dropdown)
3. Ingresar cantidad y precio aplicado
4. Backend recalcula métricas del producto
5. Reevalúa riesgo con nuevos datos
6. Muestra evaluación actualizada
7. Dashboard se actualiza

### Caso 3: Monitorear Riesgos

1. Ver tabla en dashboard
2. Productos con riesgo ALTO = acciones urgentes
3. Click en venta para ver detalles
4. Análisis se actualiza en tiempo real

---

## 🐛 Debugging

### Backend no responde

```bash
# Verificar que corre
curl http://localhost:8000/api/health

# Ver logs
# (El servidor mostrará en terminal)

# Verificar BD
psql -U postgres -d margenapp_db
\dt  # Ver tablas
```

### Frontend no ve backend

```bash
# Abrir consola del navegador (F12)
# Ver si hay errores de CORS
# Verificar que backend está en localhost:8000
```

### Errores 422 en formulario

```javascript
// Los detalles vienen en error.error.detail
// Ejemplo:
{
  "detail": [
    {
      "loc": ["body", "nombre"],
      "msg": "ensure this value has at most 100 characters",
      "type": "value_error.string.max_length"
    }
  ]
}
```

---

## 📊 Variables de Entorno

En `config.py`:

```python
DB_PARAMS = {
    "dbname": "margenapp_db",      # ← Cambiar
    "user": "postgres",             # ← Cambiar
    "password": "123",              # ← CAMBIAR EN PRODUCCIÓN
    "host": "localhost",            # ← Cambiar si BD remota
    "port": "5433"                  # ← Puerto PostgreSQL
}
```

---

## 🔒 Seguridad Checklist

- [ ] Cambiar contraseña BD en producción
- [ ] Cambiar `allow_origins=["*"]` a dominios específicos
- [ ] Usar variables de entorno (`.env`)
- [ ] Validar entrada con Pydantic ✅
- [ ] SQL parametrizado ✅
- [ ] Manejo seguro de errores ✅

---

## 📈 Escalabilidad Futura

### Fácil de agregar:

1. **Autenticación JWT**
   - Agregar middleware en `routes.py`
   - Validar token en endpoints

2. **Caché Redis**
   - Agregar servicio en `ia_service.py`
   - Caché resultados de IA

3. **Reportes**
   - Agregar métodos en `services.py`
   - Nuevos endpoints en `routes.py`

4. **Gráficos**
   - Nuevos servicios en frontend
   - Componentes nuevos

---

## 🎓 Arquitectura Aplicada

### Principios:

✅ **SRP** - Cada módulo una responsabilidad
✅ **DRY** - Sin código duplicado
✅ **SOLID** - Código limpio
✅ **Repository Pattern** - Abstracción de BD
✅ **Service Layer** - Lógica centralizada
✅ **Dependency Injection** - Módulos desacoplados

### Ventajas:

- 📊 Mejor testabilidad
- 🔧 Más mantenible
- 📈 Escalable
- ♻️ Reutilizable
- 🎯 Separación clara

---

## 📚 Documentación Completa

| Documento | Propósito |
|-----------|-----------|
| `ARQUITECTURA_REFACTORIZADA.md` | Explicación detallada |
| `CAMBIOS_Y_NUEVAS_FEATURES.md` | Qué cambió y por qué |
| `SETUP_BD.md` | Script SQL completo |
| `ENDPOINT_DOCUMENTATION.md` | Referencia de endpoints |
| `INTEGRATION_GUIDE.md` | Guía de integración |

---

## ⚙️ Configuración Producción

### Backend

```python
# config.py
CORS_ORIGINS = ["https://tudominio.com"]  # No "*"
DB_PARAMS = {
    "host": "db.servidor.com",           # BD remota
    "password": os.getenv("DB_PASSWORD") # Variable env
}
```

### Frontend

```typescript
// producto.service.ts
private apiUrl = 'https://api.tudominio.com/api';
```

### Deploy

```bash
# Backend: Docker + Gunicorn
docker build -t margenapp-backend .
docker run -p 8000:8000 margenapp-backend

# Frontend: Build para producción
ng build --configuration production
# Servir con Nginx
```

---

## 🆘 FAQs

**P: ¿Dónde está el archivo `main.py` monolítico?**
R: Fue refactorizado en 7 módulos. El nuevo `main.py` solo tiene 45 líneas.

**P: ¿Cómo agrego un nuevo endpoint?**
R: 
1. Agregar schema en `schemas.py`
2. Agregar método en `services.py`
3. Agregar ruta en `routes.py`

**P: ¿Cómo cambio a otra BD?**
R: Cambiar string de conexión en `config.py`. El código usa psycopg2, fácil migrar a MySQL cambiando el driver.

**P: ¿Por qué tarda en predecir riesgo?**
R: El modelo ML se entrena al iniciar. Usar caché en producción.

**P: ¿Cómo agrego autenticación?**
R: Implementar middleware JWT en `routes.py` que valide token.

---

## 🎉 Últimos Pasos

1. ✅ Clonar repo
2. ✅ Crear BD con `SETUP_BD.md`
3. ✅ `pip install -r requirements.txt` (backend)
4. ✅ `npm install` (frontend)
5. ✅ `python main.py` (backend)
6. ✅ `npm start` (frontend)
7. ✅ Abrir http://localhost:4200
8. ✅ ¡Crear productos y ventas!

---

**¿Necesitas ayuda?** Consulta `ARQUITECTURA_REFACTORIZADA.md` para detalles.

**¿Listo para producción?** Revisa la sección "Configuración Producción" arriba.

🚀 **¡MargenApp está lista!** 🚀
