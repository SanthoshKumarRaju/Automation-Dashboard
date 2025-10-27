import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule, NgForm } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';
import { Router } from '@angular/router';
import { SupportdashboardService } from '../../services/supportdashboard.service';
import { NgxSpinnerService } from 'ngx-spinner';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent implements OnInit {
  constructor(
    private route: Router,
    private service: SupportdashboardService,
     private spinner: NgxSpinnerService
  ) {}
  ngOnInit(): void {
  this.spinner.show();
   const id=localStorage.getItem('session_id');
   id?this.route.navigate(['']):this.route.navigate(['/login'])
   this.spinner.hide();
  }
  username: string = '';
  password: string = '';
  onSubmit(form: NgForm) {
    if (form.valid) {
      const obj = {
        username: this.username,
        password: this.password,
      };
      this.service.login_service(obj).subscribe({
        next: (data) => {
           if (data.statusCode === 200) {
          localStorage.setItem('session_id', data.access_token);
           }
        },
        error: (err) => {
          console.error('Error occurred:', err);
        },
        complete: () => {
           const id=localStorage.getItem('session_id');
           id?this.route.navigate(['']):this.route.navigate(['/login'])
        }
      });
    }
  }
}
