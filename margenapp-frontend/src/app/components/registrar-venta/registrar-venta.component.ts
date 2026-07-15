import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ProductoService, ListaProductos, VentaResponse } from '../../services/producto.service';

@Component({
  selector: 'app-registrar-venta',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './registrar-venta.component.html',
  styleUrls: ['./registrar-venta.component.css']
})
export class RegistrarVentaComponent implements OnInit {
  formularioVenta!: FormGroup;
  productos: ListaProductos[] = [];
  cargandoProductos = false;
  cargando = false;
  error: string | null = null;
  respuesta: VentaResponse | null = null;
  mostrarRespuesta = false;

  @Output() ventaRegistrada = new EventEmitter<VentaResponse>();

  constructor(
    private fb: FormBuilder,
    private productoService: ProductoService
  ) {
    this.inicializarFormulario();
  }

  ngOnInit(): void {
    this.cargarProductos();
  }

  inicializarFormulario(): void {
    this.formularioVenta = this.fb.group({
      producto_id: ['', Validators.required],
      cantidad: ['', [Validators.required, Validators.min(1)]],
      precio_aplicado: ['', [Validators.required, Validators.min(0.01)]]
    });
  }

  cargarProductos(): void {
    this.cargandoProductos = true;
    this.productoService.obtenerProductos().subscribe({
      next: (respuesta) => {
        this.productos = respuesta.productos;
        this.cargandoProductos = false;
      },
      error: (err) => {
        this.error = 'No se pudieron cargar los productos: ' + err.message;
        this.cargandoProductos = false;
      }
    });
  }

  enviarFormulario(): void {
    if (this.formularioVenta.invalid) {
      this.error = 'Por favor, completa todos los campos correctamente';
      return;
    }

    this.cargando = true;
    this.error = null;
    this.respuesta = null;

    const venta = this.formularioVenta.value;

    this.productoService.registrarVenta(venta).subscribe({
      next: (respuestaServidor) => {
        this.respuesta = respuestaServidor;
        this.mostrarRespuesta = true;
        this.cargando = false;
        
        // Limpiar formulario
        this.formularioVenta.reset();
        
        // Emitir evento para actualizar dashboard
        this.ventaRegistrada.emit(respuestaServidor);
      },
      error: (err) => {
        this.error = err.message;
        this.cargando = false;
      }
    });
  }

  resetearFormulario(): void {
    this.formularioVenta.reset();
    this.error = null;
    this.respuesta = null;
    this.mostrarRespuesta = false;
  }

  cerrarRespuesta(): void {
    this.mostrarRespuesta = false;
  }

  obtenerColorRiesgo(nivel: string): string {
    switch (nivel) {
      case 'BAJO': return 'success';
      case 'MEDIO': return 'warning';
      case 'ALTO': return 'danger';
      default: return 'secondary';
    }
  }

  obtenerIconoRiesgo(nivel: string): string {
    switch (nivel) {
      case 'BAJO': return 'check-circle-fill';
      case 'MEDIO': return 'exclamation-triangle-fill';
      case 'ALTO': return 'x-circle-fill';
      default: return 'info-circle-fill';
    }
  }

  obtenerProductoNombre(id: number): string {
    const producto = this.productos.find(p => p.id === id);
    return producto ? producto.nombre : 'N/A';
  }

  obtenerProductoPrecio(id: number): number | undefined {
    const producto = this.productos.find(p => p.id === id);
    return producto?.precio;
  }

  calcularIngresos(): number {
    const cantidad = this.formularioVenta.get('cantidad')?.value;
    const precio = this.formularioVenta.get('precio_aplicado')?.value;
    return (cantidad && precio) ? cantidad * precio : 0;
  }
}
