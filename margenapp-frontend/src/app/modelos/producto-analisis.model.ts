export interface ProductoAnalisis {
  id: number;
  nombre: string;
  categoria: string;
  precio_promedio: number;
  margen_objetivo: number;
  variacion_ventas_pct: number;
  margen_actual_pct: number;
  nivel_riesgo: 'ALTO' | 'MEDIO' | 'BAJO';
}
