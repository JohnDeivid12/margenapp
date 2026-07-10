import { Component, OnInit } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { ProductoAnalisis } from '../modelos/producto-analisis.model';
import { DashboardService } from '../services/dashboard.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, DecimalPipe],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
})
export class DashboardComponent implements OnInit {
  productos: ProductoAnalisis[] = [];
  
  // Contadores para las tarjetas del tope
  totalAlto: number = 0;
  totalMedio: number = 0;
  totalBajo: number = 0;

  constructor(private dashboardService: DashboardService) { }

  ngOnInit(): void {
    this.cargarAnalisis();
  }

  cargarAnalisis(): void {
    this.dashboardService.obtenerAnalisisRiesgo().subscribe({
      next: (data) => {
        this.productos = data;
        this.calcularContadores();
      },
      error: (err) => {
        console.error('Error conectando con el backend de Python:', err);
      }
    });
  }

  calcularContadores(): void {
    this.totalAlto = this.productos.filter(p => p.nivel_riesgo === 'ALTO').length;
    this.totalMedio = this.productos.filter(p => p.nivel_riesgo === 'MEDIO').length;
    this.totalBajo = this.productos.filter(p => p.nivel_riesgo === 'BAJO').length;
  }
}
