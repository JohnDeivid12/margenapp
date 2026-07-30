import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditarProducto } from './editar-producto.component';

describe('EditarProducto', () => {
  let component: EditarProducto;
  let fixture: ComponentFixture<EditarProducto>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditarProducto],
    }).compileComponents();

    fixture = TestBed.createComponent(EditarProducto);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
