import { Component } from '@angular/core';
import { routes } from '../../app.routes';
import { Router, RouterLink } from '@angular/router';
import { SupportdashboardService } from '../../services/supportdashboard.service';

@Component({
  selector: 'app-side-nav',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './side-nav.component.html',
  styleUrl: './side-nav.component.scss'
})
export class SideNavComponent {
  constructor(
    private route: Router,
    private apiservice: SupportdashboardService
  ) {}
logout(){    
  this.route.navigate(['/login'])
  this.apiservice.logout_service().subscribe(res=>{
    if(res){
    console.log(res)
    this.route.navigate(['/login'])
    localStorage.clear();
    sessionStorage.clear();
    }
  })
}
}
