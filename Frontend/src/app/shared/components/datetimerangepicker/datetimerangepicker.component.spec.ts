import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DatetimerangepickerComponent } from './datetimerangepicker.component';

describe('DatetimerangepickerComponent', () => {
  let component: DatetimerangepickerComponent;
  let fixture: ComponentFixture<DatetimerangepickerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DatetimerangepickerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DatetimerangepickerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
