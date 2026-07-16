import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { ProductoAnalisis } from '../modelos/producto-analisis.model';
import { DashboardService } from '../services/dashboard.service';
import { CrearProductoComponent } from '../components/crear-producto/crear-producto.component';
import { RegistrarVentaComponent } from '../components/registrar-venta/registrar-venta.component';
import { HistorialVentasComponent } from '../components/historial-ventas/historial-ventas';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule, 
    DecimalPipe, 
    CrearProductoComponent, 
    RegistrarVentaComponent,
    HistorialVentasComponent
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
})
export class DashboardComponent implements OnInit {
  productos: ProductoAnalisis[] = [];

  // Control para la Pantalla de Bienvenida Inicial
  mostrarBienvenida = true;

  // Contadores para las tarjetas del tope
  totalAlto: number = 0;
  totalMedio: number = 0;
  totalBajo: number = 0;

  // Para mostrar/ocultar los formularios
  mostrarFormularioProducto = false;
  mostrarFormularioVenta = false;

  // Propiedad para el producto seleccionado (inicialmente null)
  productoSeleccionado: any = null;

  // Referencia para comunicarnos con el componente de historial y recargarlo
  @ViewChild(HistorialVentasComponent) historialComponent!: HistorialVentasComponent;

  constructor(private dashboardService: DashboardService) { }

  ngOnInit(): void {
    this.cargarAnalisis();
  }

  /**
   * Cierra la pantalla de bienvenida y da paso al panel principal
   */
  entrarAlApp(): void {
    this.mostrarBienvenida = false;
  }

  cargarAnalisis(): void {
    this.dashboardService.obtenerAnalisisRiesgo().subscribe({
      next: (res: any) => {
        // 1. Validamos de dónde viene el arreglo.
        if (Array.isArray(res)) {
          this.productos = res;
        } else if (res && Array.isArray(res.productos)) {
          this.productos = res.productos;
        } else if (res && Array.isArray(res.data)) {
          this.productos = res.data;
        } else {
          this.productos = []; // Evitamos que sea null o undefined
        }
        // 2. Ahora sí calculamos los contadores de forma segura
        this.calcularContadores();
      },
      error: (err) => {
        console.error('Error al cargar análisis', err);
      }
    });
  }

  calcularContadores(): void {
    // Si por alguna razón productos no es un arreglo válido, detenemos la ejecución
    if (!Array.isArray(this.productos)) {
      this.totalAlto = 0;
      this.totalMedio = 0;
      this.totalBajo = 0;
      return;
    }

    // Ahora filtramos directamente con la propiedad oficial 'nivel_riesgo'
    this.totalAlto = this.productos.filter(p => p.nivel_riesgo === 'ALTO').length;
    this.totalMedio = this.productos.filter(p => p.nivel_riesgo === 'MEDIO').length;
    this.totalBajo = this.productos.filter(p => p.nivel_riesgo === 'BAJO').length;
  }

  // Crear la función para seleccionar el producto a analizar
  seleccionarProducto(producto: any): void {
    this.productoSeleccionado = producto;
  }

  /**
   * Alterna la visibilidad del formulario de creación de productos
   */
  toggleFormularioProducto(): void {
    this.mostrarFormularioProducto = !this.mostrarFormularioProducto;
  }

  /**
   * Alterna la visibilidad del formulario de registro de ventas
   */
  toggleFormularioVenta(): void {
    this.mostrarFormularioVenta = !this.mostrarFormularioVenta;
  }

  /**
   * Cierra el formulario de creación de productos
   */
  cerrarFormularioProducto(): void {
    this.mostrarFormularioProducto = false;
  }

  /**
   * Cierra el formulario de registro de ventas
   */
  cerrarFormularioVenta(): void {
    this.mostrarFormularioVenta = false;
  }

  /**
   * Recarga los datos después de crear un producto
   */
  onProductoCreado(): void {
    this.cargarAnalisis();
    this.mostrarFormularioProducto = false;
  }

  /**
   * Recarga los datos después de registrar una venta e inyecta la actualización al historial
   */
  onVentaRegistrada(): void {
    this.cargarAnalisis();
    this.mostrarFormularioVenta = false;
    
    // Si el componente de historial existe, le ordenamos refrescar la tabla de inmediato
    if (this.historialComponent) {
      this.historialComponent.obtenerHistorial();
    }
  }
}