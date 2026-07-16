import { Component, OnInit, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ProductoService } from '../../services/producto.service';

@Component({
  selector: 'app-editar-producto',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './editar-producto.component.html',
  styleUrls: ['./editar-producto.component.css'] // Puedes reutilizar los estilos de creación
})
export class EditarProductoComponent implements OnInit, OnChanges {
  form: FormGroup;
  cargando = false;
  error: string | null = null;

  // Recibe el producto seleccionado para editar desde el componente padre
  @Input() producto: any = null;

  // Eventos para notificar al componente padre
  @Output() productoEditado = new EventEmitter<any>();
  @Output() cancel = new EventEmitter<void>();

  constructor(
    private fb: FormBuilder,
    private productoService: ProductoService
  ) {
    // Inicializar el formulario con la misma estructura que tu componente de creación
    this.form = this.fb.group({
      nombre: ['', [Validators.required, Validators.maxLength(100)]],
      categoria: ['', [Validators.required, Validators.maxLength(50)]],
      precio: ['', [Validators.required, Validators.min(0.01)]],
      margen_objetivo: ['', [
        Validators.required,
        Validators.min(0),
        Validators.max(1)
      ]]
    });
  }

  ngOnInit(): void {}

  /**
   * Escucha cambios en el @Input() 'producto' para rellenar el formulario dinámicamente
   */
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['producto'] && this.producto) {
      this.form.patchValue({
        nombre: this.producto.nombre,
        categoria: this.producto.categoria,
        precio: this.producto.precio,
        margen_objetivo: this.producto.margen_objetivo
      });
    }
  }

  /**
   * Envía los cambios del formulario al backend (PUT)
   */
  enviarFormulario(): void {
    if (this.form.invalid) {
      this.error = 'Por favor, completa el formulario correctamente';
      return;
    }

    if (!this.producto || !this.producto.id) {
      this.error = 'No se ha seleccionado un producto válido';
      return;
    }

    this.cargando = true;
    this.error = null;

    // Consumir el método del servicio pasándole el ID y el cuerpo actualizado
    this.productoService.actualizarProducto(this.producto.id, this.form.value).subscribe({
      next: (response) => {
        this.cargando = false;
        console.log('✅ Producto actualizado:', response);

        // Notificar al padre que la edición fue exitosa
        this.productoEditado.emit(response);
      },
      error: (error) => {
        this.cargando = false;
        this.error = error.message || 'Error al actualizar el producto';
        console.error('❌ Error en actualización:', error);
      }
    });
  }

  /**
   * Cancela la operación sin guardar cambios
   */
  cancelar(): void {
    this.form.reset();
    this.cancel.emit();
  }

  /**
   * Métodos auxiliares heredados de tu estructura de validación
   */
  tieneError(nombreCampo: string, tipoError: string): boolean {
    const campo = this.form.get(nombreCampo);
    return !!(campo && campo.hasError(tipoError) && campo.touched);
  }

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