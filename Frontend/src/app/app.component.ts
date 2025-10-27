import { Component, OnInit } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { SideNavComponent } from './core/side-nav/side-nav.component';
import { AgGridAngular } from 'ag-grid-angular';
import { NgxSpinnerModule } from 'ngx-spinner';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NgxSpinnerModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent implements OnInit {
  constructor(private route: Router) {}
  ngOnInit(): void {
      this.route.navigate(['']);

    // if (localStorage.getItem('token')) {
    //   this.route.navigate(['']);
    // } else {
    //   this.route.navigate(['login']);
    // }
  }
}
