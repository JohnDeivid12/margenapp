import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ProductoAnalisis } from '../modelos/producto-analisis.model';


@Injectable({
  providedIn: 'root',
})
export class DashboardService {// URL exacta de tu backend en Python
  private apiUrl = 'http://127.0.0.1:8000/api/productos/analisis';

  constructor(private http: HttpClient) { }

  obtenerAnalisisRiesgo(): Observable<ProductoAnalisis[]> {
    return this.http.get<ProductoAnalisis[]>(this.apiUrl);
  }
}
