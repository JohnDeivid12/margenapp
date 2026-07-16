import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ProductoAnalisis } from '../modelos/producto-analisis.model';
import { DashboardService } from '../services/dashboard.service';
import { ProductoService } from '../services/producto.service';
import { CrearProductoComponent } from '../components/crear-producto/crear-producto.component';
import { RegistrarVentaComponent } from '../components/registrar-venta/registrar-venta.component';
import { HistorialVentasComponent } from '../components/historial-ventas/historial-ventas';
import { EditarProductoComponent } from '../components/editar-producto/editar-producto.component';
  

// Importaciones necesarias para Gráficas
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions } from 'chart.js';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule, 
    DecimalPipe, 
    FormsModule,
    CrearProductoComponent, 
    RegistrarVentaComponent,
    HistorialVentasComponent,
    EditarProductoComponent,
    BaseChartDirective
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
})
export class DashboardComponent implements OnInit {
  productos: ProductoAnalisis[] = [];

  mostrarBienvenida = true;

  totalAlto: number = 0;
  totalMedio: number = 0;
  totalBajo: number = 0;

  mostrarFormularioProducto = false;
  mostrarFormularioVenta = false;

  // <-- 3. Control de visibilidad para el formulario de edición
  mostrarFormularioEdicion = false;

  // Propiedad para el producto seleccionado (inicialmente null)
  productoSeleccionado: any = null;

  // --- CONFIGURACIÓN DE LA GRÁFICA ---
  public chartOptions: ChartOptions<'doughnut'> = { responsive: true };
  public chartData: ChartConfiguration<'doughnut'>['data'] = {
    labels: ['Riesgo Alto', 'Riesgo Medio', 'Riesgo Bajo'],
    datasets: [{ 
      data: [0, 0, 0], 
      backgroundColor: ['#dc3545', '#ffc107', '#198754'] 
    }]
  };

  @ViewChild(HistorialVentasComponent) historialComponent!: HistorialVentasComponent;

  constructor(
    private dashboardService: DashboardService,
    private productoService: ProductoService
  ) { }

  ngOnInit(): void {
    this.cargarAnalisis();
  }

  entrarAlApp(): void {
    this.mostrarBienvenida = false;
  }

  cargarAnalisis(): void {
    this.dashboardService.obtenerAnalisisRiesgo().subscribe({
      next: (res: any) => {
        if (Array.isArray(res)) {
          this.productos = res;
        } else if (res && Array.isArray(res.productos)) {
          this.productos = res.productos;
        } else if (res && Array.isArray(res.data)) {
          this.productos = res.data;
        } else {
          this.productos = [];
        }
        this.calcularContadores();
      },
      error: (err) => {
        console.error('Error al cargar análisis', err);
      }
    });
  }

  calcularContadores(): void {
    if (!Array.isArray(this.productos)) {
      this.totalAlto = 0;
      this.totalMedio = 0;
      this.totalBajo = 0;
      return;
    }

    this.totalAlto = this.productos.filter(p => p.nivel_riesgo === 'ALTO').length;
    this.totalMedio = this.productos.filter(p => p.nivel_riesgo === 'MEDIO').length;
    this.totalBajo = this.productos.filter(p => p.nivel_riesgo === 'BAJO').length;

    // IMPORTANTE: Esta línea actualiza el gráfico cada vez que cambian los contadores
    this.chartData.datasets[0].data = [this.totalAlto, this.totalMedio, this.totalBajo];
  }

  seleccionarProducto(producto: any): void {
    this.productoSeleccionado = producto;
  }

  toggleFormularioProducto(): void {
    this.mostrarFormularioProducto = !this.mostrarFormularioProducto;
  }

  toggleFormularioVenta(): void {
    this.mostrarFormularioVenta = !this.mostrarFormularioVenta;
  }

  cerrarFormularioProducto(): void {
    this.mostrarFormularioProducto = false;
  }

  cerrarFormularioVenta(): void {
    this.mostrarFormularioVenta = false;
  }

  onProductoCreado(): void {
    this.cargarAnalisis();
    this.mostrarFormularioProducto = false;
  }

  onVentaRegistrada(): void {
    this.cargarAnalisis();
    this.mostrarFormularioVenta = false;
    
    if (this.historialComponent) {
      this.historialComponent.obtenerHistorial();
    }
  }

  abrirEdicion(producto: any): void {
    this.productoSeleccionado = producto;
    this.mostrarFormularioEdicion = true;
    
    // Si tienes abiertos los otros formularios, los cerramos para no saturar la UI
    this.mostrarFormularioProducto = false;
    this.mostrarFormularioVenta = false;
  }

  /**
   * Cierra el panel de edición limpiando el producto activo
   */
  cerrarEdicion(): void {
    this.mostrarFormularioEdicion = false;
    this.productoSeleccionado = null;
  }

  /**
   * Se ejecuta cuando el componente hijo termina la petición PUT con éxito
   */
  onProductoEditado(response: any): void {
    this.cargarAnalisis(); // Recarga los datos en caliente desde PostgreSQL (recalculando IA)
    this.cerrarEdicion();  // Cierra el formulario de edición
  }

  eliminarProducto(producto: any): void {
    if (!producto?.id) return;

    const ok = window.confirm(`¿Seguro que deseas eliminar "${producto.nombre}"? Esta acción no se puede deshacer.`);
    if (!ok) return;

    this.productoService.eliminarProducto(producto.id).subscribe({
      next: () => {
        if (this.productoSeleccionado?.id === producto.id) {
          this.productoSeleccionado = null;
          this.mostrarFormularioEdicion = false;
        }
        this.cargarAnalisis();
        if (this.historialComponent) {
          this.historialComponent.obtenerHistorial();
        }
      },
      error: (err) => {
        console.error('Error al eliminar producto', err);
        alert(err?.message || 'Error al eliminar el producto');
      }
    });
  }
}