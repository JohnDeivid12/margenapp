import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ProductoService, ProductoResponse } from '../../services/producto.service';

@Component({
  selector: 'app-crear-producto',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './crear-producto.component.html',
  styleUrls: ['./crear-producto.component.css']
})
export class CrearProductoComponent implements OnInit {
  form: FormGroup;
  cargando = false;
  respuesta: ProductoResponse | null = null;
  error: string | null = null;
  mostrarRespuesta = false;

  // EventEmitter para notificar al padre cuando se crea un producto
  @Output() productCreated = new EventEmitter<ProductoResponse>();

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

        // Emitir evento para notificar al dashboard
        this.productCreated.emit(response);

        // Mostrar notificación de éxito (opcional)
        this.mostrarNotificacion('Producto creado exitosamente', 'success');
      },
      (error) => {
        // Error
        this.cargando = false;
        this.error = error.message;
        this.mostrarRespuesta = false;

        console.error('❌ Error:', error);

        // Si 'this.error' es nulo, enviará 'Error desconocido'
        this.mostrarNotificacion(this.error || 'Ocurrió un error', 'error');
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
    // Implementar con: npm install ngx-toastr
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
