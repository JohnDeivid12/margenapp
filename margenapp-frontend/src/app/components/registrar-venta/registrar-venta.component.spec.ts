import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { RegistrarVentaComponent } from './registrar-venta.component';
import { ProductoService } from '../../services/producto.service';
import { of, throwError } from 'rxjs';

describe('RegistrarVentaComponent', () => {
  let component: RegistrarVentaComponent;
  let fixture: ComponentFixture<RegistrarVentaComponent>;
  let productoService: jasmine.SpyObj<ProductoService>;

  beforeEach(async () => {
    const spy = jasmine.createSpyObj('ProductoService', [
      'obtenerProductos',
      'registrarVenta',
      'obtenerVentas'
    ]);

    await TestBed.configureTestingModule({
      imports: [RegistrarVentaComponent, ReactiveFormsModule, HttpClientTestingModule],
      providers: [
        { provide: ProductoService, useValue: spy }
      ]
    }).compileComponents();

    productoService = TestBed.inject(ProductoService) as jasmine.SpyObj<ProductoService>;
    fixture = TestBed.createComponent(RegistrarVentaComponent);
    component = fixture.componentInstance;
  });

  it('debe crear el componente', () => {
    expect(component).toBeTruthy();
  });

  it('debe cargar productos al inicializar', () => {
    const productosTest = {
      productos: [
        { id: 1, nombre: 'Laptop', categoria: 'Electrónica', precio: 1200, margen_objetivo: 0.2 }
      ],
      total: 1
    };

    productoService.obtenerProductos.and.returnValue(of(productosTest));

    component.ngOnInit();

    expect(productoService.obtenerProductos).toHaveBeenCalled();
    expect(component.productos.length).toBe(1);
    expect(component.productos[0].nombre).toBe('Laptop');
  });

  it('debe mostrar error si no carga los productos', () => {
    productoService.obtenerProductos.and.returnValue(
      throwError(() => new Error('Error de conexión'))
    );

    component.cargarProductos();

    expect(component.error).toContain('No se pudieron cargar los productos');
  });

  it('debe validar que el formulario sea requerido', () => {
    component.inicializarFormulario();
    expect(component.formularioVenta.invalid).toBeTruthy();
  });

  it('debe calcular ingresos correctamente', () => {
    component.formularioVenta.patchValue({
      cantidad: 5,
      precio_aplicado: 1000
    });

    const ingresos = component.calcularIngresos();
    expect(ingresos).toBe(5000);
  });

  it('debe rechazar cantidad negativa', () => {
    component.formularioVenta.patchValue({
      cantidad: -1,
      precio_aplicado: 100
    });

    expect(component.formularioVenta.invalid).toBeTruthy();
  });

  it('debe rechazar precio cero', () => {
    component.formularioVenta.patchValue({
      cantidad: 5,
      precio_aplicado: 0
    });

    expect(component.formularioVenta.invalid).toBeTruthy();
  });

  it('debe registrar una venta exitosamente', () => {
    const ventaTest = {
      id: 1,
      producto_id: 1,
      cantidad: 5,
      precio_aplicado: 1150,
      fecha_venta: '2024-07-14',
      nivel_riesgo_actualizado: 'BAJO',
      probabilidad_riesgo_actualizado: 15,
      mensaje: '✅ Riesgo bajo'
    };

    productoService.registrarVenta.and.returnValue(of(ventaTest));

    component.formularioVenta.patchValue({
      producto_id: 1,
      cantidad: 5,
      precio_aplicado: 1150
    });

    component.enviarFormulario();

    expect(productoService.registrarVenta).toHaveBeenCalled();
    expect(component.respuesta).toEqual(ventaTest);
    expect(component.mostrarRespuesta).toBeTruthy();
  });

  it('debe emitir evento cuando la venta es registrada', (done) => {
    const ventaTest = {
      id: 1,
      producto_id: 1,
      cantidad: 5,
      precio_aplicado: 1150,
      fecha_venta: '2024-07-14',
      nivel_riesgo_actualizado: 'BAJO',
      probabilidad_riesgo_actualizado: 15,
      mensaje: '✅ Riesgo bajo'
    };

    productoService.registrarVenta.and.returnValue(of(ventaTest));

    component.ventaRegistrada.subscribe((venta) => {
      expect(venta).toEqual(ventaTest);
      done();
    });

    component.formularioVenta.patchValue({
      producto_id: 1,
      cantidad: 5,
      precio_aplicado: 1150
    });

    component.enviarFormulario();
  });

  it('debe resetear el formulario', () => {
    component.formularioVenta.patchValue({
      producto_id: 1,
      cantidad: 5,
      precio_aplicado: 1150
    });

    component.resetearFormulario();

    expect(component.formularioVenta.get('producto_id')?.value).toBeNull();
    expect(component.error).toBeNull();
    expect(component.respuesta).toBeNull();
  });

  it('debe obtener color de riesgo correcto', () => {
    expect(component.obtenerColorRiesgo('BAJO')).toBe('success');
    expect(component.obtenerColorRiesgo('MEDIO')).toBe('warning');
    expect(component.obtenerColorRiesgo('ALTO')).toBe('danger');
  });
});
