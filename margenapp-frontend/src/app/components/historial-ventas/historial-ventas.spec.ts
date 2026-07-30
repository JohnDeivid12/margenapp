import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HistorialVentasComponent } from './historial-ventas';

describe('HistorialVentasComponent', () => {
  let component: HistorialVentasComponent;
  let fixture: ComponentFixture<HistorialVentasComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HistorialVentasComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HistorialVentasComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});