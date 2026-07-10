import { Component, signal } from '@angular/core';
import { DashboardComponent } from './dashboard/dashboard.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [DashboardComponent],
  template: '<app-dashboard></app-dashboard>',
  styleUrls: ['./app.css']
})
export class App {
  protected readonly title = signal('margenapp-frontend');
}
