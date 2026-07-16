import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ProductoService } from '../../services/producto.service'; // <-- Vinculamos el servicio de tu equipo

interface Venta {
  id: number;
  producto_id: number;
  producto_nombre: string;
  cantidad: number;
  precio_aplicado: number;
  fecha_venta: string;
}

@Component({
  selector: 'app-historial-ventas',
  standalone: true,
  imports: [CommonModule], // <-- Retiramos HttpClientModule innecesario aquí
  templateUrl: './historial-ventas.html',
  styleUrls: ['./historial-ventas.css']
})
export class HistorialVentasComponent implements OnInit {
  ventas: Venta[] = [];
  cargando = false;
  error: string | null = null;

  constructor(
    private productoService: ProductoService, // <-- Inyectamos el servicio oficial
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.obtenerHistorial();
  }

  obtenerHistorial(): void {
    this.cargando = true;
    this.error = null;

    /**
     * IMPORTANTE:
     * Si tu compañero definió un método específico en 'ProductoService' para traer las ventas, 
     * su nombre habitual sería 'obtenerVentas()' o similar.
     * 
     * Si al escribir "this.productoService." la ayuda visual de VS Code te sugiere algo relacionado,
     * cámbialo por ese nombre. Si no, usamos 'obtenerProductos()' por defecto para mapear las ventas.
     */
    this.productoService.obtenerVentas().subscribe({
      next: (respuesta: any) => {
        // Adaptamos los datos si la API los devuelve con un formato "respuesta.ventas"
        if (respuesta && Array.isArray(respuesta.ventas)) {
          this.ventas = respuesta.ventas;
        } else if (Array.isArray(respuesta)) {
          this.ventas = respuesta;
        } else {
          this.ventas = [];
        }
        
        this.cargando = false;
        this.cdr.detectChanges(); // Forzamos a Angular a redibujar tu bonita tabla
      },
      error: (err) => {
        console.error('Error cargando historial en componente:', err);
        this.error = 'No se pudo cargar el historial de ventas.';
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }
}