import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { CrearProductoComponent } from './crear-producto.component';
import { ProductoService } from '../../services/producto.service';

describe('CrearProductoComponent', () => {
  let component: CrearProductoComponent;
  let fixture: ComponentFixture<CrearProductoComponent>;
  let productoService: ProductoService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CrearProductoComponent, ReactiveFormsModule, HttpClientTestingModule],
      providers: [ProductoService]
    }).compileComponents();

    fixture = TestBed.createComponent(CrearProductoComponent);
    component = fixture.componentInstance;
    productoService = TestBed.inject(ProductoService);
    fixture.detectChanges();
  });

  it('debe crear el componente', () => {
    expect(component).toBeTruthy();
  });

  it('debe validar el formulario correctamente', () => {
    const form = component.form;
    
    // Inicialmente debe ser inválido
    expect(form.invalid).toBeTruthy();
    
    // Llenar con datos válidos
    form.patchValue({
      nombre: 'Laptop',
      categoria: 'Electrónica',
      precio: 1200,
      margen_objetivo: 0.20,
      cantidad_inicial: 10
    });
    
    // Ahora debe ser válido
    expect(form.valid).toBeTruthy();
  });

  it('debe rechazar precio negativo', () => {
    const form = component.form;
    form.patchValue({ precio: -100 });
    expect(form.get('precio')?.invalid).toBeTruthy();
  });

  it('debe rechazar margen > 1', () => {
    const form = component.form;
    form.patchValue({ margen_objetivo: 1.5 });
    expect(form.get('margen_objetivo')?.invalid).toBeTruthy();
  });

  it('debe formatear margen como porcentaje', () => {
    const resultado = component.formatearMargen(0.25);
    expect(resultado).toBe('25.0%');
  });

  it('debe obtener el icono correcto para BAJO', () => {
    component.respuesta = {
      id: 1,
      nombre: 'Test',
      categoria: 'Test',
      precio: 100,
      margen_objetivo: 0.25,
      cantidad_inicial: 0,
      nivel_riesgo: 'BAJO',
      probabilidad_riesgo: 5,
      mensaje: 'Test',
      fecha_creacion: new Date().toISOString()
    };
    expect(component.obtenerIconoRiesgo()).toBe('✅');
  });

  it('debe resetar el formulario', () => {
    component.form.patchValue({
      nombre: 'Laptop',
      categoria: 'Electrónica',
      precio: 1200
    });
    component.error = 'Test error';
    component.mostrarRespuesta = true;

    component.resetarFormulario();

    expect(component.form.get('nombre')?.value).toBeNull();
    expect(component.error).toBeNull();
    expect(component.mostrarRespuesta).toBeFalsy();
  });
});
