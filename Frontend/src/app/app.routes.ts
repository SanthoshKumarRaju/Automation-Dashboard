import { Routes } from '@angular/router';
import { LoginComponent } from './core/login/login.component';
import { main } from './features/main/main.routes'

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
   ...main, 
  {path: '', redirectTo: 'login', pathMatch: 'full'},
];
