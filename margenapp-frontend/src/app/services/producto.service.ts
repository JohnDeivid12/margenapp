import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

// ============================================================================
// INTERFACES DE PRODUCTOS
// ============================================================================

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

export interface ListaProductos {
  id: number;
  nombre: string;
  categoria: string;
  precio: number;
  margen_objetivo: number;
}

export interface AnalisisResponse {
  productos: ProductoResponse[];
  total: number;
}

export interface ListaProductosResponse {
  productos: ListaProductos[];
  total: number;
}

// ============================================================================
// INTERFACES DE VENTAS
// ============================================================================

export interface VentaRequest {
  producto_id: number;
  cantidad: number;
  precio_aplicado: number;
}

export interface VentaResponse {
  id: number;
  producto_id: number;
  cantidad: number;
  precio_aplicado: number;
  fecha_venta: string;
  nivel_riesgo_actualizado: string;
  probabilidad_riesgo_actualizado: number;
  mensaje: string;
}

export interface VentasResponse {
  ventas: any[];
  total: number;
}

@Injectable({
  providedIn: 'root'
})
export class ProductoService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  // ============================================================================
  // MÉTODOS DE PRODUCTOS
  // ============================================================================

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
  obtenerAnalisis(): Observable<AnalisisResponse> {
    return this.http.get<AnalisisResponse>(`${this.apiUrl}/productos/analisis`).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene la lista de productos (sin análisis detallado)
   * Útil para dropdowns/selects en formularios
   * @returns Observable con lista de productos básica
   */
  obtenerProductos(): Observable<ListaProductosResponse> {
    return this.http.get<ListaProductosResponse>(`${this.apiUrl}/productos/lista`).pipe(
      catchError(this.handleError)
    );
  }

 // ✅ Corregido — genera http://localhost:8000/api/productos/1
actualizarProducto(id: number, productoData: any): Observable<any> {
  return this.http.put(`${this.apiUrl}/productos/${id}`, productoData).pipe(
    catchError(this.handleError)
  );
}

eliminarProducto(id: number): Observable<any> {
  return this.http.delete(`${this.apiUrl}/productos/${id}`).pipe(
    catchError(this.handleError)
  );
}

  // ============================================================================
  // MÉTODOS DE VENTAS
  // ============================================================================

  /**
   * Registra una nueva venta
   * @param venta Datos de la venta
   * @returns Observable con respuesta del servidor
   */
  registrarVenta(venta: VentaRequest): Observable<VentaResponse> {
    return this.http.post<VentaResponse>(
      `${this.apiUrl}/ventas/registrar`,
      venta
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene todas las ventas registradas
   * @returns Observable con lista de ventas
   */
  obtenerVentas(): Observable<VentasResponse> {
    return this.http.get<VentasResponse>(`${this.apiUrl}/ventas/todas`).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene las ventas de un producto específico
   * @param productoId ID del producto
   * @returns Observable con lista de ventas del producto
   */
  obtenerVentasPorProducto(productoId: number): Observable<VentasResponse> {
    return this.http.get<VentasResponse>(`${this.apiUrl}/ventas/producto/${productoId}`).pipe(
      catchError(this.handleError)
    );
  }

  // ============================================================================
  // MÉTODOS DE SALUD
  // ============================================================================

  /**
   * Verifica que el backend esté disponible
   * @returns Observable con estado del servidor
   */
  verificarSalud(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`).pipe(
      catchError(this.handleError)
    );
  }

  // ============================================================================
  // MANEJO DE ERRORES
  // ============================================================================

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
            .map((err: any) => `${err.loc.join('.')}: ${err.msg}`)
            .join('; ');
        }
      } else if (error.status === 503) {
        errorMessage = 'Base de datos no disponible';
      } else if (error.status === 500) {
        errorMessage = error.error?.detail || 'Error interno del servidor';
      } else if (error.status === 404) {
        errorMessage = error.error?.detail || 'Recurso no encontrado';
      } else {
        errorMessage = `Error ${error.status}: ${error.statusText}`;
      }
    }

    console.error('❌ Error HTTP:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
