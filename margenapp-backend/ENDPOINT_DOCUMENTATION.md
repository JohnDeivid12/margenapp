# 📚 Documentación - Endpoint POST /api/productos/crear

## Descripción General

Este endpoint recibe datos del formulario de Angular, realiza validaciones automáticas con Pydantic, guarda los datos en PostgreSQL y ejecuta el algoritmo predictivo para evaluar el nivel de riesgo del producto.

---

## 🔗 Endpoint

**URL:** `POST http://localhost:8000/api/productos/crear`

---

## 📝 Estructura del Request

### Headers
```http
Content-Type: application/json
```

### Body (JSON)
```json
{
  "nombre": "Laptop Dell XPS 13",
  "categoria": "Electrónica",
  "precio": 1200.00,
  "margen_objetivo": 0.20,
  "cantidad_inicial": 10
}
```

### Campos

| Campo | Tipo | Requerido | Validaciones | Ejemplo |
|-------|------|-----------|--------------|---------|
| `nombre` | string | ✅ Sí | Min 1 car, Max 100 car | "Laptop Dell XPS 13" |
| `categoria` | string | ✅ Sí | Min 1 car, Max 50 car | "Electrónica" |
| `precio` | float | ✅ Sí | Debe ser > 0 | 1200.00 |
| `margen_objetivo` | float | ✅ Sí | Entre 0 y 1 (0-100%) | 0.20 |
| `cantidad_inicial` | int | ❌ No | >= 0 (default: 0) | 10 |

---

## ✅ Validaciones Automáticas (Pydantic)

Pydantic valida automáticamente ANTES de que el request llegue al endpoint:

1. **Nombre:**
   - ❌ No puede estar vacío
   - ❌ No puede exceder 100 caracteres
   - ✅ Se elimina espacios en blanco al inicio/final

2. **Categoría:**
   - ❌ No puede estar vacía
   - ❌ No puede exceder 50 caracteres
   - ✅ Se elimina espacios en blanco al inicio/final

3. **Precio:**
   - ❌ Debe ser un número positivo (> 0)
   - ❌ No se acepta precio = 0 o negativo

4. **Margen Objetivo:**
   - ✅ Debe estar entre 0 y 1 (representa 0-100%)
   - ❌ No se aceptan valores fuera de ese rango

5. **Cantidad Inicial:**
   - ✅ Debe ser >= 0
   - ✅ Por defecto es 0 si no se proporciona

---

## 📤 Response (Exitoso)

**Status Code:** `201 Created`

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

### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | int | ID único del producto en la BD |
| `nombre` | string | Nombre del producto (validado) |
| `categoria` | string | Categoría del producto (validada) |
| `precio` | float | Precio unitario |
| `margen_objetivo` | float | Margen objetivo (0-1) |
| `cantidad_inicial` | int | Cantidad inicial en inventario |
| `nivel_riesgo` | string | **BAJO**, **MEDIO** o **ALTO** |
| `probabilidad_riesgo` | float | Porcentaje de probabilidad (0-100) |
| `mensaje` | string | Recomendación personalizada |
| `fecha_creacion` | string | Fecha/hora ISO 8601 |

---

## ❌ Errores Posibles

### 1. Validación Fallida (400 Bad Request)

**Caso:** Precio negativo
```json
{
  "detail": [
    {
      "loc": ["body", "precio"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

**Caso:** Margen fuera de rango
```json
{
  "detail": [
    {
      "loc": ["body", "margen_objetivo"],
      "msg": "ensure this value is less than or equal to 1",
      "type": "value_error.number.not_le"
    }
  ]
}
```

### 2. Error de Base de Datos (500 Internal Server Error)

```json
{
  "detail": "Error al guardar el producto: (psycopg2.ProgrammingError) relation \"productos\" does not exist"
}
```

### 3. Error de Conexión (503 Service Unavailable)

```json
{
  "detail": "Error de conexión a base de datos: could not connect to server"
}
```

---

## 🎯 Flujo del Endpoint

```
1. Angular envía POST con JSON
        ↓
2. Pydantic valida automáticamente (ProductoCreate)
        ↓
3. Si validación falla → Retorna 400 Bad Request
        ↓
4. Si validación OK → Conecta a PostgreSQL
        ↓
5. Guarda el producto (INSERT)
        ↓
6. Ejecuta algoritmo predictivo con el margen_objetivo
        ↓
7. Retorna ProductoResponse (201 Created)
```

---

## 🔍 Ejemplo: Integración con Angular (HttpClient)

### TypeScript Service

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ProductoRequest {
  nombre: string;
  categoria: string;
  precio: number;
  margen_objetivo: number;
  cantidad_inicial?: number;
}

export interface ProductoResponse {
  id: number;
  nombre: string;
  categoria: string;
  precio: number;
  margen_objetivo: number;
  cantidad_inicial: number;
  nivel_riesgo: 'BAJO' | 'MEDIO' | 'ALTO';
  probabilidad_riesgo: number;
  mensaje: string;
  fecha_creacion: string;
}

@Injectable({
  providedIn: 'root'
})
export class ProductoService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  crearProducto(producto: ProductoRequest): Observable<ProductoResponse> {
    return this.http.post<ProductoResponse>(
      `${this.apiUrl}/productos/crear`,
      producto
    );
  }
}
```

### Component Example

```typescript
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ProductoService } from './services/producto.service';

@Component({
  selector: 'app-crear-producto',
  templateUrl: './crear-producto.component.html',
  styleUrls: ['./crear-producto.component.css']
})
export class CrearProductoComponent {
  form: FormGroup;
  cargando = false;
  respuesta: any = null;
  error: string | null = null;

  constructor(
    private fb: FormBuilder,
    private productoService: ProductoService
  ) {
    this.form = this.fb.group({
      nombre: ['', [Validators.required, Validators.maxLength(100)]],
      categoria: ['', [Validators.required, Validators.maxLength(50)]],
      precio: ['', [Validators.required, Validators.min(0.01)]],
      margen_objetivo: ['', [Validators.required, Validators.min(0), Validators.max(1)]],
      cantidad_inicial: [0, Validators.min(0)]
    });
  }

  enviarFormulario() {
    if (this.form.invalid) {
      this.error = 'Por favor, completa el formulario correctamente';
      return;
    }

    this.cargando = true;
    this.error = null;
    this.respuesta = null;

    this.productoService.crearProducto(this.form.value).subscribe(
      (response) => {
        this.respuesta = response;
        this.cargando = false;
        this.form.reset({ cantidad_inicial: 0 });
        console.log('✅ Producto creado:', response);
      },
      (error) => {
        this.cargando = false;
        this.error = error.error?.detail || 'Error al crear el producto';
        console.error('❌ Error:', error);
      }
    );
  }
}
```

### HTML Template

```html
<div class="container">
  <h2>Crear Nuevo Producto</h2>

  <form [formGroup]="form" (ngSubmit)="enviarFormulario()">
    <!-- Nombre -->
    <div class="form-group">
      <label for="nombre">Nombre del Producto *</label>
      <input
        id="nombre"
        type="text"
        formControlName="nombre"
        placeholder="ej: Laptop Dell XPS 13"
        maxlength="100"
      />
      <small *ngIf="form.get('nombre')?.hasError('required')">
        El nombre es requerido
      </small>
    </div>

    <!-- Categoría -->
    <div class="form-group">
      <label for="categoria">Categoría *</label>
      <input
        id="categoria"
        type="text"
        formControlName="categoria"
        placeholder="ej: Electrónica"
        maxlength="50"
      />
      <small *ngIf="form.get('categoria')?.hasError('required')">
        La categoría es requerida
      </small>
    </div>

    <!-- Precio -->
    <div class="form-group">
      <label for="precio">Precio (USD) *</label>
      <input
        id="precio"
        type="number"
        formControlName="precio"
        placeholder="1200.00"
        step="0.01"
        min="0"
      />
      <small *ngIf="form.get('precio')?.hasError('required')">
        El precio es requerido
      </small>
      <small *ngIf="form.get('precio')?.hasError('min')">
        El precio debe ser mayor a 0
      </small>
    </div>

    <!-- Margen Objetivo -->
    <div class="form-group">
      <label for="margen">Margen Objetivo (0-1) *</label>
      <input
        id="margen"
        type="number"
        formControlName="margen_objetivo"
        placeholder="0.20"
        step="0.01"
        min="0"
        max="1"
      />
      <small>Ej: 0.20 = 20%, 0.50 = 50%</small>
      <small *ngIf="form.get('margen_objetivo')?.hasError('required')">
        El margen es requerido
      </small>
    </div>

    <!-- Cantidad Inicial -->
    <div class="form-group">
      <label for="cantidad">Cantidad Inicial</label>
      <input
        id="cantidad"
        type="number"
        formControlName="cantidad_inicial"
        placeholder="10"
        min="0"
      />
    </div>

    <!-- Botón Enviar -->
    <button type="submit" [disabled]="form.invalid || cargando">
      {{ cargando ? 'Guardando...' : 'Crear Producto' }}
    </button>
  </form>

  <!-- Error -->
  <div *ngIf="error" class="alert alert-error">
    ❌ {{ error }}
  </div>

  <!-- Respuesta Exitosa -->
  <div *ngIf="respuesta" class="alert alert-success">
    <h3>✅ Producto Creado Exitosamente</h3>
    <p><strong>ID:</strong> {{ respuesta.id }}</p>
    <p><strong>Nombre:</strong> {{ respuesta.nombre }}</p>
    <p><strong>Nivel de Riesgo:</strong>
      <span [class]="'badge-' + respuesta.nivel_riesgo.toLowerCase()">
        {{ respuesta.nivel_riesgo }}
      </span>
    </p>
    <p><strong>Probabilidad:</strong> {{ respuesta.probabilidad_riesgo | number:'1.1-1' }}%</p>
    <p><strong>Recomendación:</strong> {{ respuesta.mensaje }}</p>
  </div>
</div>
```

---

## 📊 Niveles de Riesgo

### BAJO (Nivel 0)
- ✅ Margen saludable (> 20%)
- ✅ Bajo riesgo de pérdida
- 📈 Continuar monitoreando

### MEDIO (Nivel 1)
- ⚠️ Margen aceptable (5-20%)
- ⚠️ Riesgo moderado
- 🔧 Considerar ajustes de costos

### ALTO (Nivel 2)
- 🔴 Margen crítico (< 5%)
- 🔴 Alto riesgo de pérdida
- 🚨 Acción inmediata recomendada

---

## 🧪 Testing con cURL

```bash
# Request exitoso
curl -X POST http://localhost:8000/api/productos/crear \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop Dell XPS 13",
    "categoria": "Electrónica",
    "precio": 1200.00,
    "margen_objetivo": 0.20,
    "cantidad_inicial": 10
  }'

# Request con precio inválido
curl -X POST http://localhost:8000/api/productos/crear \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Producto",
    "categoria": "Test",
    "precio": -100,
    "margen_objetivo": 0.20
  }'

# Request con margen fuera de rango
curl -X POST http://localhost:8000/api/productos/crear \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Producto",
    "categoria": "Test",
    "precio": 100,
    "margen_objetivo": 1.5
  }'
```

---

## 🔌 Otros Endpoints

### GET /api/productos/analisis
Obtiene análisis de riesgo para todos los productos registrados.

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

### GET /api/health
Verifica que el servidor esté activo.

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

## 📋 Requisitos de BD

La tabla `productos` debe existir en PostgreSQL con esta estructura:

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

---

## 🚀 Iniciar el Backend

```bash
cd margenapp-backend
python -m pip install -r requirements.txt  # Si existe requirements.txt
python main.py
```

El servidor estará disponible en: `http://localhost:8000`
API Docs (Swagger): `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

---

## 📝 Notas Importantes

1. **Pydantic valida automáticamente** - No necesitas validar manualmente en el endpoint
2. **Las excepciones se manejan automáticamente** - FastAPI retorna errores 4xx/5xx adecuados
3. **CORS está habilitado** - El frontend Angular puede consumir la API sin problemas (en producción cambiar allow_origins)
4. **La conexión a BD se cierra siempre** - Usa try/finally para garantizar limpieza
5. **El modelo de IA se entrena al iniciar** - Se carga en memoria para mejor rendimiento

