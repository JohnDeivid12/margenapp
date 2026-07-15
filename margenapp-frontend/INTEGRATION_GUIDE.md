# 🎨 MargenApp Frontend - Angular Integration

Este documento describe cómo usar la integración del componente `CrearProductoComponent` con el backend FastAPI.

---

## 📦 Estructura de Archivos Creados

```
src/app/
├── components/
│   └── crear-producto/
│       ├── crear-producto.component.ts         ✨ Componente principal
│       ├── crear-producto.component.html       🎯 Template HTML
│       ├── crear-producto.component.css        🎨 Estilos
│       └── crear-producto.component.spec.ts    🧪 Tests
├── services/
│   ├── producto.service.ts                     🔗 Servicio HTTP
│   └── producto.service.spec.ts                🧪 Tests servicio
└── dashboard/
    ├── dashboard.component.ts                  ✅ (Actualizado)
    └── dashboard.component.html                ✅ (Actualizado)
```

---

## 🚀 Quick Start

### 1. Instalar Dependencias

```bash
cd margenapp-frontend
npm install
```

### 2. Iniciar Frontend

```bash
npm start
```

El frontend estará disponible en `http://localhost:4200`

### 3. Verificar Backend

Asegúrate que el backend FastAPI esté corriendo:

```bash
cd ../margenapp-backend
python main.py
```

Backend debe estar en `http://localhost:8000`

---

## 🎯 Componentes Creados

### 1. ProductoService (servicio/producto.service.ts)

Servicio que gestiona las llamadas HTTP al backend:

```typescript
// Crear producto
crearProducto(producto: ProductoRequest): Observable<ProductoResponse>

// Obtener análisis
obtenerAnalisis(): Observable<AnalisisResponse>

// Verificar salud del backend
verificarSalud(): Observable<any>
```

### 2. CrearProductoComponent

Componente standalone que:
- ✅ Muestra formulario de creación de productos
- ✅ Valida datos con FormControl de Angular
- ✅ Envía datos al backend
- ✅ Muestra evaluación de riesgo
- ✅ Emite evento cuando se crea un producto

**Props:**
- `@Output() productCreated` - Emitido cuando se crea un producto

**Métodos públicos:**
- `enviarFormulario()` - Envía el formulario al backend
- `resetarFormulario()` - Limpia el formulario
- `obtenerColorRiesgo()` - Retorna color Bootstrap para el nivel de riesgo
- `formatearMargen()` - Formatea margen como porcentaje
- `obtenerIconoRiesgo()` - Retorna icono para el nivel de riesgo

---

## 🔌 Integración en Dashboard

El componente está integrado en el dashboard:

```html
<!-- En dashboard.component.html -->
<button (click)="toggleFormulario()" class="btn btn-primary">
  Nuevo Producto
</button>

<!-- Formulario modal -->
<div *ngIf="mostrarFormulario">
  <app-crear-producto (productCreated)="onProductoCreado()"></app-crear-producto>
</div>
```

**Dashboard methods:**
- `toggleFormulario()` - Muestra/oculta el formulario
- `cerrarFormulario()` - Cierra el formulario
- `onProductoCreado()` - Recarga datos después de crear producto

---

## 📋 Validaciones Angular (Frontend)

El formulario valida en el cliente ANTES de enviar:

```typescript
// Campos validados
nombre:            required, maxLength(100)
categoria:         required, maxLength(50)
precio:            required, min(0.01)
margen_objetivo:   required, min(0), max(1)
cantidad_inicial:  min(0), default=0
```

---

## 📡 Request/Response

### Request al Backend

```typescript
interface ProductoRequest {
  nombre: string;                  // ej: "Laptop Dell"
  categoria: string;               // ej: "Electrónica"
  precio: number;                  // ej: 1200.00
  margen_objetivo: number;         // ej: 0.20 (20%)
  cantidad_inicial?: number;       // ej: 10 (opcional)
}
```

### Response del Backend

```typescript
interface ProductoResponse {
  id: number;
  nombre: string;
  categoria: string;
  precio: number;
  margen_objetivo: number;
  cantidad_inicial: number;
  nivel_riesgo: 'BAJO' | 'MEDIO' | 'ALTO';
  probabilidad_riesgo: number;     // 0-100%
  mensaje: string;                 // Recomendación
  fecha_creacion: string;          // ISO 8601
}
```

---

## 🎨 Interfaz de Usuario

### Formulario
- Campo de nombre con validación
- Campo de categoría con validación
- Campo de precio con símbolo $
- Campo de margen con símbolo %
- Campo de cantidad (opcional)
- Botones: Crear Producto, Limpiar

### Respuesta
- Card con resultado exitoso (verde)
- Badge de nivel de riesgo con color:
  - **BAJO** 🟢 Verde
  - **MEDIO** 🟡 Amarillo
  - **ALTO** 🔴 Rojo
- Progress bar del margen
- Mensaje de recomendación
- Fecha de creación formateada

### Errores
- Alert rojo si falla validación del backend
- Mensajes descriptivos para cada error
- Campo requerido marca con clase `.is-invalid`

---

## 🧪 Testing

### Ejecutar Tests

```bash
npm test
```

### Tests Incluidos

**Componente:**
- Validación de formulario
- Rechazo de datos inválidos
- Formateo de margen
- Reseteo de formulario
- Obtención de iconos correctos

**Servicio:**
- Creación de producto
- Obtención de análisis
- Verificación de salud
- Manejo de errores HTTP

---

## 🔒 Seguridad

✅ Validación en cliente (UX rápida)
✅ Validación en servidor (Pydantic)
✅ Tipado fuerte con TypeScript
✅ CORS habilitado en backend
✅ Manejo seguro de errores

---

## 🐛 Troubleshooting

### ❌ "Backend no disponible"

1. Verifica que backend esté corriendo:
```bash
curl http://localhost:8000/api/health
```

2. Si falla, inicia el backend:
```bash
cd ../margenapp-backend
python main.py
```

### ❌ "Error 422 Unprocessable Entity"

Los datos no cumplen validaciones del backend:
- Precio debe ser > 0
- Margen debe estar entre 0 y 1
- Nombre no puede estar vacío

### ❌ "CORS error"

Backend debe permitir el origen de Angular. En `main.py`:

```python
allow_origins=["http://localhost:4200"]
```

### ❌ "No se ve Bootstrap"

1. Verifica que Bootstrap esté importado en `src/styles.css`:
```css
@import 'node_modules/bootstrap/dist/css/bootstrap.min.css';
```

2. Reinicia el servidor:
```bash
npm start
```

---

## 🎓 Cómo Funciona

1. **Usuario rellena formulario** en `CrearProductoComponent`
2. **Angular valida localmente** con FormControl validators
3. **Usuario hace click en "Crear"** → `enviarFormulario()`
4. **ProductoService.crearProducto()** envía POST al backend
5. **Backend valida con Pydantic** → SQL INSERT → IA Predict
6. **Backend retorna ProductoResponse** con resultado
7. **Component.subscribe()** recibe datos
8. **HTML renderiza resultado** (nivel de riesgo, etc)
9. **Emitir evento productCreated** para notificar dashboard
10. **Dashboard.onProductoCreado()** recarga lista de productos

---

## 📊 Flujo Visual

```
┌─────────────────────────────────┐
│  Usuario llena formulario       │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Angular valida formalmente     │
│  - max length                   │
│  - tipo de dato                 │
│  - rango de valores             │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Usuario hace click "Crear"     │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  ProductoService.crearProducto()│
│  POST /api/productos/crear      │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Backend (FastAPI)              │
│  - Pydantic valida              │
│  - PostgreSQL INSERT            │
│  - Scikit-Learn predice riesgo  │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Response: ProductoResponse     │
│  HTTP 201 Created               │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Component recibe respuesta     │
│  - Mostrar nivel de riesgo      │
│  - Mostrar recomendación        │
│  - Emitir evento productCreated │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Dashboard recibe evento        │
│  - Recarga lista de productos   │
│  - Cierra formulario            │
│  - Actualiza contadores         │
└─────────────────────────────────┘
```

---

## 🔗 API Endpoints Usados

```
POST   http://localhost:8000/api/productos/crear      ← Crear
GET    http://localhost:8000/api/productos/analisis   ← Listar
GET    http://localhost:8000/api/health               ← Verificar
```

---

## 📚 Documentación Completa

Ver archivos en `margenapp-backend/`:
- `README.md` - Instalación backend
- `ENDPOINT_DOCUMENTATION.md` - API detallada
- `ANGULAR_INTEGRATION.md` - Integración (este documento)
- `ARCHITECTURE.md` - Diagramas

---

## 🚀 Próximos Pasos

- [ ] Listar todos los productos en tabla
- [ ] Editar producto (PUT)
- [ ] Eliminar producto (DELETE)
- [ ] Paginación
- [ ] Filtros y búsqueda
- [ ] Exportar a CSV/PDF
- [ ] Gráficos de riesgo
- [ ] Autenticación JWT

---

## 📞 Soporte

Si encuentras problemas:

1. Verifica que backend esté corriendo
2. Abre la consola del navegador (F12) y busca errores
3. Verifica los logs del backend en terminal
4. Consulta troubleshooting section arriba

---

**¡Listo para usar! 🎉**
