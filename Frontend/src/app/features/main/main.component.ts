import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SideNavComponent } from '../../core/side-nav/side-nav.component';

@Component({
  selector: 'app-main',
  standalone: true,
  imports: [RouterOutlet, SideNavComponent],
  templateUrl: './main.component.html',
  styleUrl: './main.component.scss'
})
export class MainComponent {

}
