import { Routes } from '@angular/router';
import { LoginComponent } from '../../core/login/login.component';
import { AuditFrameworkComponent } from '../audit-framework/audit-framework.component';
import { StoreLocationsComponent } from '../store-locations/store-locations.component';
import { StoreUsersComponent } from '../store-users/store-users.component';
import { MainComponent } from './main.component';

export const main: Routes = [
  {
    path: '',
    component: MainComponent, // Main layout
    children: [
      // { path: '', component: StoreLocationsComponent }, // default feature
      { path: 'store-locations', component: StoreLocationsComponent },
      { path: 'store-users', component: StoreUsersComponent },
      { path: 'audit-framework', component: AuditFrameworkComponent },
    ],
  },
];
