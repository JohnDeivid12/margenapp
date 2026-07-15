# 🔗 Integración con Angular

Guía completa para integrar el endpoint POST del backend con componentes Angular.

---

## 📦 Step 1: Crear el Servicio

Crear archivo: `src/app/services/producto.service.ts`

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

// Interfaces que coinciden con Pydantic
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

  /**
   * Crea un nuevo producto
   * @param producto Datos del producto
   * @returns Observable con respuesta del servidor
   */
  crearProducto(producto: ProductoRequest): Observable<ProductoResponse> {
    return this.http.post<ProductoResponse>(
      `${this.apiUrl}/productos/crear`,
      producto
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene análisis de riesgo de todos los productos
   * @returns Observable con lista de productos
   */
  obtenerAnalisis(): Observable<any> {
    return this.http.get(`${this.apiUrl}/productos/analisis`).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Verifica que el backend esté disponible
   * @returns Observable con estado del servidor
   */
  verificarSalud(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Manejo centralizado de errores HTTP
   */
  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'Error desconocido';

    if (error.error instanceof ErrorEvent) {
      // Error del lado del cliente
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Error del lado del servidor
      if (error.status === 422) {
        // Validación fallida
        const validationErrors = error.error.detail;
        if (Array.isArray(validationErrors)) {
          errorMessage = validationErrors
            .map(err => `${err.loc.join('.')}: ${err.msg}`)
            .join('; ');
        }
      } else if (error.status === 503) {
        errorMessage = 'Base de datos no disponible';
      } else if (error.status === 500) {
        errorMessage = error.error?.detail || 'Error interno del servidor';
      } else {
        errorMessage = `Error ${error.status}: ${error.statusText}`;
      }
    }

    console.error('❌ Error HTTP:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
```

---

## 🎨 Step 2: Crear el Componente

Crear archivo: `src/app/components/crear-producto/crear-producto.component.ts`

```typescript
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ProductoService, ProductoResponse } from '../../services/producto.service';

@Component({
  selector: 'app-crear-producto',
  templateUrl: './crear-producto.component.html',
  styleUrls: ['./crear-producto.component.css']
})
export class CrearProductoComponent implements OnInit {
  form: FormGroup;
  cargando = false;
  respuesta: ProductoResponse | null = null;
  error: string | null = null;
  mostrarRespuesta = false;

  // Para colorear el nivel de riesgo
  colorRiesgo: { [key: string]: string } = {
    'BAJO': 'success',
    'MEDIO': 'warning',
    'ALTO': 'danger'
  };

  constructor(
    private fb: FormBuilder,
    private productoService: ProductoService
  ) {
    this.form = this.fb.group({
      nombre: ['', [Validators.required, Validators.maxLength(100)]],
      categoria: ['', [Validators.required, Validators.maxLength(50)]],
      precio: ['', [Validators.required, Validators.min(0.01)]],
      margen_objetivo: ['', [
        Validators.required,
        Validators.min(0),
        Validators.max(1)
      ]],
      cantidad_inicial: [0, [Validators.min(0)]]
    });
  }

  ngOnInit(): void {
    // Verificar que el backend está disponible
    this.productoService.verificarSalud().subscribe(
      (response) => console.log('✅ Backend disponible:', response),
      (error) => console.error('❌ Backend no disponible:', error)
    );
  }

  /**
   * Envía el formulario al backend
   */
  enviarFormulario(): void {
    // Validar que el formulario sea válido
    if (this.form.invalid) {
      this.error = 'Por favor, completa el formulario correctamente';
      this.mostrarRespuesta = false;
      return;
    }

    // Mostrar estado de carga
    this.cargando = true;
    this.error = null;
    this.respuesta = null;
    this.mostrarRespuesta = false;

    // Llamar al servicio
    this.productoService.crearProducto(this.form.value).subscribe(
      (response: ProductoResponse) => {
        // Éxito
        this.respuesta = response;
        this.cargando = false;
        this.mostrarRespuesta = true;
        this.form.reset({ cantidad_inicial: 0 });
        
        console.log('✅ Producto creado:', response);
        
        // Mostrar notificación de éxito (opcional)
        this.mostrarNotificacion('Producto creado exitosamente', 'success');
      },
      (error) => {
        // Error
        this.cargando = false;
        this.error = error.message;
        this.mostrarRespuesta = false;
        
        console.error('❌ Error:', error);
        
        // Mostrar notificación de error (opcional)
        this.mostrarNotificacion(this.error, 'error');
      }
    );
  }

  /**
   * Resetea el formulario y la respuesta
   */
  resetarFormulario(): void {
    this.form.reset({ cantidad_inicial: 0 });
    this.respuesta = null;
    this.error = null;
    this.mostrarRespuesta = false;
  }

  /**
   * Muestra una notificación (requiere librería como ng-toastr)
   */
  private mostrarNotificacion(mensaje: string, tipo: 'success' | 'error'): void {
    // Implementar con: npm install ng-toastr
    console.log(`[${tipo.toUpperCase()}] ${mensaje}`);
  }

  /**
   * Obtiene el color Bootstrap para el nivel de riesgo
   */
  obtenerColorRiesgo(): string {
    if (!this.respuesta) return 'secondary';
    return this.colorRiesgo[this.respuesta.nivel_riesgo] || 'secondary';
  }

  /**
   * Formatea el margen como porcentaje
   */
  formatearMargen(valor: number): string {
    return (valor * 100).toFixed(1) + '%';
  }

  /**
   * Obtiene icono según el nivel de riesgo
   */
  obtenerIconoRiesgo(): string {
    if (!this.respuesta) return '?';
    switch (this.respuesta.nivel_riesgo) {
      case 'BAJO':
        return '✅';
      case 'MEDIO':
        return '⚠️';
      case 'ALTO':
        return '🔴';
      default:
        return '❓';
    }
  }

  /**
   * Verifica si un campo tiene error
   */
  tieneError(nombreCampo: string, tipoError: string): boolean {
    const campo = this.form.get(nombreCampo);
    return !!(campo && campo.hasError(tipoError) && campo.touched);
  }

  /**
   * Obtiene mensaje de error para un campo
   */
  obtenerMensajeError(nombreCampo: string): string {
    const campo = this.form.get(nombreCampo);
    
    if (campo?.hasError('required')) {
      return 'Este campo es requerido';
    }
    if (campo?.hasError('maxlength')) {
      const maxLength = campo.getError('maxlength').requiredLength;
      return `Máximo ${maxLength} caracteres`;
    }
    if (campo?.hasError('min')) {
      const minValue = campo.getError('min').min;
      return `Mínimo ${minValue}`;
    }
    if (campo?.hasError('max')) {
      const maxValue = campo.getError('max').max;
      return `Máximo ${maxValue}`;
    }
    
    return 'Error de validación';
  }
}
```

---

## 🎯 Step 3: HTML Template

Crear archivo: `src/app/components/crear-producto/crear-producto.component.html`

```html
<div class="container mt-5">
  <div class="row">
    <div class="col-lg-6">
      <!-- FORMULARIO -->
      <div class="card">
        <div class="card-header bg-primary text-white">
          <h4 class="mb-0">📝 Crear Nuevo Producto</h4>
        </div>

        <form [formGroup]="form" (ngSubmit)="enviarFormulario()" class="card-body">
          
          <!-- Campo: Nombre -->
          <div class="form-group mb-3">
            <label for="nombre" class="form-label">Nombre del Producto *</label>
            <input
              id="nombre"
              type="text"
              class="form-control"
              [class.is-invalid]="tieneError('nombre', 'required')"
              formControlName="nombre"
              placeholder="ej: Laptop Dell XPS 13"
              maxlength="100"
            />
            <small class="form-text text-muted">
              Máximo 100 caracteres
            </small>
            <div class="invalid-feedback" *ngIf="tieneError('nombre', 'required')">
              {{ obtenerMensajeError('nombre') }}
            </div>
          </div>

          <!-- Campo: Categoría -->
          <div class="form-group mb-3">
            <label for="categoria" class="form-label">Categoría *</label>
            <input
              id="categoria"
              type="text"
              class="form-control"
              [class.is-invalid]="tieneError('categoria', 'required')"
              formControlName="categoria"
              placeholder="ej: Electrónica"
              maxlength="50"
            />
            <small class="form-text text-muted">
              Máximo 50 caracteres
            </small>
            <div class="invalid-feedback" *ngIf="tieneError('categoria', 'required')">
              {{ obtenerMensajeError('categoria') }}
            </div>
          </div>

          <!-- Campo: Precio -->
          <div class="form-group mb-3">
            <label for="precio" class="form-label">Precio (USD) *</label>
            <div class="input-group">
              <span class="input-group-text">$</span>
              <input
                id="precio"
                type="number"
                class="form-control"
                [class.is-invalid]="tieneError('precio', 'required') || tieneError('precio', 'min')"
                formControlName="precio"
                placeholder="1200.00"
                step="0.01"
                min="0"
              />
            </div>
            <small class="form-text text-muted">
              Debe ser mayor a $0
            </small>
            <div class="invalid-feedback" 
              *ngIf="tieneError('precio', 'required') || tieneError('precio', 'min')">
              {{ obtenerMensajeError('precio') }}
            </div>
          </div>

          <!-- Campo: Margen Objetivo -->
          <div class="form-group mb-3">
            <label for="margen" class="form-label">Margen Objetivo (%)*</label>
            <div class="input-group">
              <input
                id="margen"
                type="number"
                class="form-control"
                [class.is-invalid]="tieneError('margen_objetivo', 'required') || 
                                   tieneError('margen_objetivo', 'min') || 
                                   tieneError('margen_objetivo', 'max')"
                formControlName="margen_objetivo"
                placeholder="0.20"
                step="0.01"
                min="0"
                max="1"
              />
              <span class="input-group-text">%</span>
            </div>
            <small class="form-text text-muted">
              Entre 0 y 100% (ej: 0.20 = 20%, 0.50 = 50%)
            </small>
            <div class="invalid-feedback" 
              *ngIf="tieneError('margen_objetivo', 'required') || 
                     tieneError('margen_objetivo', 'min') ||
                     tieneError('margen_objetivo', 'max')">
              {{ obtenerMensajeError('margen_objetivo') }}
            </div>
          </div>

          <!-- Campo: Cantidad Inicial -->
          <div class="form-group mb-4">
            <label for="cantidad" class="form-label">Cantidad Inicial (opcional)</label>
            <input
              id="cantidad"
              type="number"
              class="form-control"
              [class.is-invalid]="tieneError('cantidad_inicial', 'min')"
              formControlName="cantidad_inicial"
              placeholder="10"
              min="0"
            />
            <small class="form-text text-muted">
              Cantidad inicial en inventario (por defecto: 0)
            </small>
          </div>

          <!-- Botones -->
          <div class="d-grid gap-2 d-md-flex justify-content-md-end">
            <button
              type="submit"
              class="btn btn-primary"
              [disabled]="form.invalid || cargando"
            >
              <span *ngIf="!cargando">🚀 Crear Producto</span>
              <span *ngIf="cargando">
                <span class="spinner-border spinner-border-sm me-2"></span>
                Guardando...
              </span>
            </button>
            <button
              type="button"
              class="btn btn-secondary"
              (click)="resetarFormulario()"
              [disabled]="cargando"
            >
              🔄 Limpiar
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- RESPUESTA Y RESULTADOS -->
    <div class="col-lg-6">
      
      <!-- Error -->
      <div *ngIf="error" class="alert alert-danger alert-dismissible fade show" role="alert">
        <h4 class="alert-heading">❌ Error</h4>
        <p class="mb-0">{{ error }}</p>
        <button type="button" class="btn-close" (click)="error = null"></button>
      </div>

      <!-- Respuesta Exitosa -->
      <div *ngIf="mostrarRespuesta && respuesta" class="card border-success">
        <div class="card-header bg-success text-white">
          <h5 class="mb-0">✅ Producto Creado Exitosamente</h5>
        </div>

        <div class="card-body">
          
          <!-- Datos del Producto -->
          <div class="row mb-3">
            <div class="col-md-6">
              <strong>ID:</strong>
              <p class="text-muted">{{ respuesta.id }}</p>
            </div>
            <div class="col-md-6">
              <strong>Nombre:</strong>
              <p class="text-muted">{{ respuesta.nombre }}</p>
            </div>
          </div>

          <div class="row mb-3">
            <div class="col-md-6">
              <strong>Categoría:</strong>
              <p class="text-muted">{{ respuesta.categoria }}</p>
            </div>
            <div class="col-md-6">
              <strong>Precio:</strong>
              <p class="text-muted">${{ respuesta.precio | number:'1.2-2' }}</p>
            </div>
          </div>

          <hr />

          <!-- Análisis de Riesgo -->
          <h6 class="mb-3">📊 Evaluación de Riesgo</h6>

          <div class="alert" [class]="'alert-' + obtenerColorRiesgo()">
            <div class="d-flex align-items-center justify-content-between">
              <div>
                <h4 class="mb-1">
                  {{ obtenerIconoRiesgo() }} Nivel de Riesgo: 
                  <strong>{{ respuesta.nivel_riesgo }}</strong>
                </h4>
                <p class="mb-0 small">
                  Probabilidad: {{ respuesta.probabilidad_riesgo | number:'1.1-1' }}%
                </p>
              </div>
            </div>
          </div>

          <!-- Margen -->
          <div class="mb-3">
            <strong>Margen Objetivo:</strong>
            <div class="progress" style="height: 25px;">
              <div
                class="progress-bar"
                [style.width.%]="respuesta.margen_objetivo * 100"
                role="progressbar"
              >
                {{ formatearMargen(respuesta.margen_objetivo) }}
              </div>
            </div>
          </div>

          <!-- Recomendación -->
          <div class="alert alert-info">
            <strong>💡 Recomendación:</strong>
            <p class="mb-0 mt-2">{{ respuesta.mensaje }}</p>
          </div>

          <!-- Fecha -->
          <small class="text-muted">
            <strong>Creado:</strong> {{ respuesta.fecha_creacion | date:'short' }}
          </small>
        </div>

        <div class="card-footer bg-light">
          <button class="btn btn-outline-primary btn-sm" (click)="resetarFormulario()">
            ➕ Crear Otro Producto
          </button>
        </div>
      </div>
    </div>
  </div>
</div>
```

---

## 🎨 Step 4: CSS Styles

Crear archivo: `src/app/components/crear-producto/crear-producto.component.css`

```css
/* General */
.container {
  max-width: 1200px;
  margin: 0 auto;
}

.form-control:focus,
.input-group-text {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

.form-control.is-invalid {
  border-color: #dc3545;
}

.form-control.is-invalid:focus {
  border-color: #dc3545;
  box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
}

/* Tarjetas */
.card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 0.5rem;
  transition: box-shadow 0.3s ease;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  font-weight: 600;
  padding: 1rem 1.5rem;
}

/* Botones */
.btn {
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);
}

/* Progress bar */
.progress {
  background-color: #e9ecef;
  border-radius: 0.25rem;
}

.progress-bar {
  background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.875rem;
}

/* Alertas */
.alert {
  border-radius: 0.5rem;
  border-left: 4px solid;
  animation: slideIn 0.3s ease;
}

.alert-success {
  border-left-color: #198754;
  background-color: #f1f5f3;
}

.alert-danger {
  border-left-color: #dc3545;
  background-color: #f8d7da;
}

.alert-warning {
  border-left-color: #ffc107;
  background-color: #fff3cd;
}

.alert-info {
  border-left-color: #0dcaf0;
  background-color: #d1ecf1;
}

/* Animaciones */
@keyframes slideIn {
  from {
    transform: translateX(-20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Labels */
.form-label {
  font-weight: 500;
  color: #495057;
  margin-bottom: 0.5rem;
}

/* Campos requeridos */
.form-label::after {
  content: '';
}

/* Spinner */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.2em;
}

/* Responsive */
@media (max-width: 768px) {
  .container {
    padding: 0 1rem;
  }

  .card {
    margin-bottom: 2rem;
  }

  .btn {
    width: 100%;
    margin-bottom: 0.5rem;
  }
}
```

---

## 📋 Step 5: Configurar HttpClientModule

En `src/app/app.module.ts`:

```typescript
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { CrearProductoComponent } from './components/crear-producto/crear-producto.component';

@NgModule({
  declarations: [
    AppComponent,
    CrearProductoComponent
  ],
  imports: [
    BrowserModule,
    ReactiveFormsModule,
    HttpClientModule  // ← Importante
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

---

## 🚀 Step 6: Usar el Componente

En `src/app/app.component.html`:

```html
<nav class="navbar navbar-dark bg-dark">
  <div class="container-fluid">
    <span class="navbar-brand mb-0 h1">🎯 MargenApp</span>
  </div>
</nav>

<app-crear-producto></app-crear-producto>
```

---

## 🧪 Step 7: Testing del Componente

Crear archivo: `src/app/components/crear-producto/crear-producto.component.spec.ts`

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { CrearProductoComponent } from './crear-producto.component';
import { ProductoService } from '../../services/producto.service';

describe('CrearProductoComponent', () => {
  let component: CrearProductoComponent;
  let fixture: ComponentFixture<CrearProductoComponent>;
  let productoService: ProductoService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [CrearProductoComponent],
      imports: [ReactiveFormsModule, HttpClientTestingModule],
      providers: [ProductoService]
    }).compileComponents();

    fixture = TestBed.createComponent(CrearProductoComponent);
    component = fixture.componentInstance;
    productoService = TestBed.inject(ProductoService);
    fixture.detectChanges();
  });

  it('debe crear el componente', () => {
    expect(component).toBeTruthy();
  });

  it('debe validar el formulario correctamente', () => {
    const form = component.form;
    
    // Inicialmente debe ser inválido
    expect(form.invalid).toBeTruthy();
    
    // Llenar con datos válidos
    form.patchValue({
      nombre: 'Laptop',
      categoria: 'Electrónica',
      precio: 1200,
      margen_objetivo: 0.20,
      cantidad_inicial: 10
    });
    
    // Ahora debe ser válido
    expect(form.valid).toBeTruthy();
  });

  it('debe rechazar precio negativo', () => {
    const form = component.form;
    form.patchValue({ precio: -100 });
    expect(form.get('precio')?.invalid).toBeTruthy();
  });

  it('debe rechazar margen > 1', () => {
    const form = component.form;
    form.patchValue({ margen_objetivo: 1.5 });
    expect(form.get('margen_objetivo')?.invalid).toBeTruthy();
  });
});
```

---

## 🔐 Seguridad

### CORS en Producción

Cambiar en `main.py`:
```python
allow_origins=[
    "https://tu-dominio.com",
    "https://www.tu-dominio.com"
]
```

### HTTPS

Usar siempre HTTPS en producción:
```typescript
private apiUrl = 'https://api.tu-dominio.com/api';
```

### Validación en Cliente

Angular proporciona validación local, pero **siempre validar en servidor** también.

---

## 📊 Flujo Completo de Integración

```
Usuario rellena formulario
        ↓
Angular valida localmente (FormControl validators)
        ↓
Usuario hace click en "Crear Producto"
        ↓
Component.enviarFormulario()
        ↓
Verificar form.valid
        ↓
ProductoService.crearProducto(formValue)
        ↓
HttpClient.post() al backend
        ↓
Backend valida con Pydantic
        ↓
Backend guarda en BD y ejecuta IA
        ↓
Backend retorna ProductoResponse (HTTP 201)
        ↓
Angular subscribe() recibe respuesta
        ↓
Component actualiza: respuesta, mostrarRespuesta = true
        ↓
HTML renderiza los resultados
        ↓
Usuario ve el nivel de riesgo y recomendación
```

---

## 💡 Tips y Mejores Prácticas

1. **Manejo de errores**: Siempre usar `catchError()` en observables
2. **Loading state**: Mostrar spinner mientras se procesa
3. **Validación dual**: Cliente (UX rápida) + Servidor (seguridad)
4. **Tipos TypeScript**: Usar interfaces que coincidan con Pydantic
5. **Caché**: Usar HttpClient interceptors para cachear
6. **Rate limiting**: Proteger contra múltiples requests
7. **Logging**: Usar console.log/error para debugging
8. **Testing**: Tests unitarios para servicios y componentes

