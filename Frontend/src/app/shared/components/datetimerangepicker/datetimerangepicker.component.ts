import { CommonModule } from '@angular/common';
import { Component, OnInit, ViewChild, Output, Input, EventEmitter, HostListener, ElementRef, OnChanges, TemplateRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatIcon } from '@angular/material/icon';
import { NgbCalendar, NgbDate, NgbDateParserFormatter, NgbDatepicker, NgbDateStruct, NgbPopover, NgbTimepicker } from '@ng-bootstrap/ng-bootstrap';
import { DayTemplateContext } from '@ng-bootstrap/ng-bootstrap/datepicker/datepicker-day-template-context';

@Component({
  selector: 'app-datetimerangepicker',
  templateUrl: './datetimerangepicker.component.html',
  styleUrls: ['./datetimerangepicker.component.scss'],
  standalone: true,
  imports: [NgbDatepicker, NgbTimepicker, NgbPopover,CommonModule,FormsModule,MatIcon],
})
export class DatetimerangepickerComponent implements OnInit, OnChanges {
  constructor(private calendar: NgbCalendar, public formatter: NgbDateParserFormatter, private eRef: ElementRef) {
    this.fromDate = calendar.getToday();
    this.toDate = calendar.getToday();
    var todayFromDate = new Date();
    todayFromDate.setHours(0, 0, 0, 0);
    var todayToDate = new Date();
    todayToDate.setHours(23, 59, 59, 0);
    this.fromTime = todayFromDate;
    this.toTime = todayToDate;

    const now = new Date();
    this.fromHour = now.getHours();
    this.fromMinute = now.getMinutes();
    this.fromSecond = now.getSeconds();

    this.toHour = 23;
    this.toMinute = 59;
    this.toSecond = 59;
  }
  hours = Array.from({ length: 24 }, (_, i) => i);
  minutes = Array.from({ length: 60 }, (_, i) => i);
  seconds = Array.from({ length: 60 }, (_, i) => i);

  fromHour = 0;
  fromMinute = 0;
  fromSecond = 0;

  toHour = 23;
  toMinute = 59;
  toSecond = 59;

  startdate: NgbDateStruct;
  enddate: NgbDateStruct;

  startTime = { hour: 0, minute: 0, second: 0 };
  endTime = { hour: 23, minute: 59, second: 59 };
  @Output() dateTimeRangeSelected = new EventEmitter<{ fDate: string, fTime: string, tDate: string, tTime: string }>();
  @Input('selectedDateTimeRange') selectedDateTimeRange: any;
  @Input('openPopover') openPopover: any;
  startDate: any;
  endDate: any;
  @ViewChild('popOver') public popover: NgbPopover;
  @ViewChild('fromDP') fromDP: NgbDatepicker;
  @ViewChild('toDP') toDP: NgbDatepicker;
  fromDate: NgbDate;
  toDate: NgbDate;
  @ViewChild('fromTP') fromTP: NgbTimepicker;
  @ViewChild('toTP') toTP: NgbTimepicker;
  fromTime: Date;
  toTime: Date;
  @Input('maxDate') maxDate: NgbDate;
  @Input('minDate') minDate: NgbDate;

  ngOnInit() {
    if (!this.maxDate) {
      this.maxDate = this.calendar.getToday();
    }
  }

  ngOnChanges() {
    if (this.openPopover) {
      setTimeout(() => {
        this.popover.open();
      }, 0);
      this.openPopover = false;
    }
  }

  // ok() {
  //   this.dateTimeRangeSelected.emit({
  //     fDate: this.formatter.format(this.fromDate),
  //     fTime: ("0" + this.fromTime.getHours()).slice(-2) + ":" + ("0" + this.fromTime.getMinutes()).slice(-2) + ":" + ("0" + this.fromTime.getSeconds()).slice(-2),
  //     tDate: this.formatter.format(this.toDate),
  //     tTime: ("0" + this.toTime.getHours()).slice(-2) + ":" + ("0" + this.toTime.getMinutes()).slice(-2) + ":" + ("0" + this.toTime.getSeconds()).slice(-2),
  //   });
  //   this.popover.close();
  // }

  ok() {
    // Sync hour, minute, second values with ngModel-bound time
    this.fromHour = this.startTime.hour;
    this.fromMinute = this.startTime.minute;
    this.fromSecond = this.startTime.second;

    this.toHour = this.endTime.hour;
    this.toMinute = this.endTime.minute;
    this.toSecond = this.endTime.second;

    const fromTime = this.getCombinedDateTime(this.fromDate, {
      hour: this.fromHour,
      minute: this.fromMinute,
      second: this.fromSecond
    });

    const toTime = this.getCombinedDateTime(this.toDate, {
      hour: this.toHour,
      minute: this.toMinute,
      second: this.toSecond
    });

    this.dateTimeRangeSelected.emit({
      fDate: this.formatter.format(this.fromDate),
      fTime: this.formatTimeString(fromTime),
      tDate: this.formatter.format(this.toDate),
      tTime: this.formatTimeString(toTime)
    });

    this.popover.close();
  }


  cancel() {
    this.popover.close();
  }

  formatTimeString(date: Date): string {
    return ("0" + date.getHours()).slice(-2) + ":" +
      ("0" + date.getMinutes()).slice(-2) + ":" +
      ("0" + date.getSeconds()).slice(-2);
  }

  getCombinedDateTime(date: NgbDateStruct, time: any): Date {
    return new Date(date.year, date.month - 1, date.day, time.hour, time.minute, time.second);
  }

  @HostListener('document:click', ['$event'])
  clickout(event) {
    if (this.eRef.nativeElement.contains(event.target) || event.target.closest("ngb-popover-window") !== null) {
      // clicked inside component or popover
    } else if (this.popover.isOpen()) {
      const fromTime = this.getCombinedDateTime(this.fromDate, {
        hour: this.fromHour,
        minute: this.fromMinute,
        second: this.fromSecond
      });

      const toTime = this.getCombinedDateTime(this.toDate, {
        hour: this.toHour,
        minute: this.toMinute,
        second: this.toSecond
      });

      this.dateTimeRangeSelected.emit({
        fDate: this.formatter.format(this.fromDate),
        fTime: this.formatTimeString(fromTime),
        tDate: this.formatter.format(this.toDate),
        tTime: this.formatTimeString(toTime)
      });

      this.popover.close();
    }
  }

  updateDateTimeDisplay() {
    const fromTime = this.getCombinedDateTime(this.fromDate, {
      hour: this.fromHour,
      minute: this.fromMinute,
      second: this.fromSecond
    });

    const toTime = this.getCombinedDateTime(this.toDate, {
      hour: this.toHour,
      minute: this.toMinute,
      second: this.toSecond
    });

    this.dateTimeRangeSelected.emit({
      fDate: this.formatter.format(this.fromDate),
      fTime: this.formatTimeString(fromTime),
      tDate: this.formatter.format(this.toDate),
      tTime: this.formatTimeString(toTime)
    });
  }


}
