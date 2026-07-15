import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ProductoService, ProductoRequest } from './producto.service';

describe('ProductoService', () => {
  let service: ProductoService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ProductoService]
    });

    service = TestBed.inject(ProductoService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('debe estar creado', () => {
    expect(service).toBeTruthy();
  });

  it('debe crear un producto', () => {
    const productoRequest: ProductoRequest = {
      nombre: 'Laptop',
      categoria: 'Electrónica',
      precio: 1200,
      margen_objetivo: 0.20
    };

    const expectedResponse = {
      id: 1,
      nombre: 'Laptop',
      categoria: 'Electrónica',
      precio: 1200,
      margen_objetivo: 0.20,
      cantidad_inicial: 0,
      nivel_riesgo: 'BAJO' as const,
      probabilidad_riesgo: 5.2,
      mensaje: 'Test',
      fecha_creacion: new Date().toISOString()
    };

    service.crearProducto(productoRequest).subscribe(response => {
      expect(response).toEqual(expectedResponse);
    });

    const req = httpMock.expectOne('http://localhost:8000/api/productos/crear');
    expect(req.request.method).toBe('POST');
    req.flush(expectedResponse);
  });

  it('debe obtener análisis de productos', () => {
    const expectedResponse = {
      productos: [],
      total: 0
    };

    service.obtenerAnalisis().subscribe(response => {
      expect(response).toEqual(expectedResponse);
    });

    const req = httpMock.expectOne('http://localhost:8000/api/productos/analisis');
    expect(req.request.method).toBe('GET');
    req.flush(expectedResponse);
  });

  it('debe verificar salud del servidor', () => {
    const expectedResponse = {
      status: '✅ MargenApp Backend está en línea'
    };

    service.verificarSalud().subscribe(response => {
      expect(response).toEqual(expectedResponse);
    });

    const req = httpMock.expectOne('http://localhost:8000/api/health');
    expect(req.request.method).toBe('GET');
    req.flush(expectedResponse);
  });

  it('debe manejar errores HTTP 422', () => {
    const error = new ErrorEvent('Network error', {
      message: 'Validation failed'
    });

    service.crearProducto({
      nombre: '',
      categoria: '',
      precio: -100,
      margen_objetivo: 1.5
    }).subscribe(
      () => fail('Should have failed with 422 error'),
      (error: Error) => {
        expect(error.message).toBeTruthy();
      }
    );
  });
});
