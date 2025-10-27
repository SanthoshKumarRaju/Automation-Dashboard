import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgSelectModule } from '@ng-select/ng-select';

@Component({
  selector: 'app-input-field',
  standalone: true,
  imports: [FormsModule, NgSelectModule, CommonModule],
  templateUrl: './input-field.component.html',
  styleUrl: './input-field.component.scss'
})
export class InputFieldComponent {

  @Input() label: string = '';            // Dynamic label for the input field
  @Input() id: string = '';               // Dynamic ID for the input field
  @Input() placeholder: string = '';      // Dynamic placeholder text
  @Input() type: string = 'text';         // Default to text input type
  @Input() value: any = '';               // Value to bind to the input field
  @Input() options: any[] | undefined = [];          // Options for the dropdown

  @Output() valueChange = new EventEmitter<any>();  // Event to emit value change

  onValueChange(newValue: any) {
    this.valueChange.emit(newValue);
  }

}
