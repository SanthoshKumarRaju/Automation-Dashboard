import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Component, Inject, PLATFORM_ID } from '@angular/core';
import { InputFieldComponent } from '../../shared/components/input-field/input-field.component';
import * as _ from 'lodash';
import moment from 'moment';
import { ColDef, GridOptions } from 'ag-grid-community';
import { AgGridModule } from 'ag-grid-angular';
import { NgbCalendar, NgbDate } from '@ng-bootstrap/ng-bootstrap';
import { NgxSpinnerModule, NgxSpinnerService } from 'ngx-spinner';
import { SupportdashboardService } from '../../services/supportdashboard.service';
import { Bootstrap_Theme, DefaultColDef, getAuditColumnDefs, getStoreColumnDefs } from '../../shared/models/gridmodel';
import { FormsModule } from '@angular/forms';
import { DatetimerangepickerComponent } from '../../shared/components/datetimerangepicker/datetimerangepicker.component';
import { ToastrService } from 'ngx-toastr';
import { environment } from '../../../environments/environment';
import { HttpResponse } from '@angular/common/http';

@Component({
  selector: 'app-audit-framework',
  standalone: true,
  imports: [
    CommonModule, InputFieldComponent, AgGridModule, FormsModule, DatetimerangepickerComponent, NgxSpinnerModule
  ],
  templateUrl: './audit-framework.component.html',
  styleUrls: ['./audit-framework.component.scss']
})
export class AuditFrameworkComponent {
  isCollapsed: boolean = true;
  selectedDate: any;
  placement = "bottom-right";
  isBrowser: boolean;
  openPopover: any;
  hasData: boolean = false;
  public columnDefs: any[] = [];
  functionalities: { label: string, value: any }[] = [];
  eventTypes: { label: string, value: any }[] = [];
  public bt_theme: any = Bootstrap_Theme
  public defaultColDef: any = DefaultColDef;
  selectedAdditionalData: any = null;
  showPopup = false;
  searchOlderThan90Days: boolean = false;

  inputFields = [
    { label: 'Company', id: 'companyId', placeholder: 'Select Company', value: '', type: 'dropdown', options: [] },
    { label: 'Store', id: 'storeId', placeholder: 'Select Store', value: '', type: 'dropdown', options: [] },
    { label: 'User', id: 'user', placeholder: 'Enter UserName', value: '', type: 'text', options: [] },
    { label: 'Functionality', id: 'functionality', placeholder: 'Select Functionality', value: '', type: 'dropdown', options: [] },
    { label: 'Event Type', id: 'eventType', placeholder: 'Select EventType', value: '', type: 'dropdown', options: [] },
    { label: 'Message', id: 'message', placeholder: 'Enter message', value: '', type: 'text', options: [] },
    { label: 'Search Audits older than 90Days', placeholder: '', id: 'check', value: false, type: 'checkbox' }
  ];

  public rowData = [
    { make: 'Tesla', model: 'Model Y', price: 64950, electric: true },
    { make: 'Ford', model: 'F-Series', price: 33850, electric: false },
    { make: 'Toyota', model: 'Corolla', price: 29600, electric: false },
  ];

  minDate: NgbDate;
  maxDate: NgbDate;
  selectedDateTimeRange: any;
  inputDate = moment().format('MM-DD-YYYY');
  inputEndDate = moment().format('MM-DD-YYYY');
  gridApi: any;
  gridColumnApi: any;
  public gridOptions: GridOptions = {};
  modalSizeClass = 'modal-dialog';
  companyList: any;
  companies: any;
  storeList: any;
  stores: any;
  selectedCompanyId: any;

  constructor(@Inject(PLATFORM_ID) private platformId: any,
    @Inject(NgxSpinnerService) private spinner: NgxSpinnerService,
    private calendar: NgbCalendar, private toaster: ToastrService,
    private supportdashboardService: SupportdashboardService
  ) {
    this.isBrowser = isPlatformBrowser(this.platformId);
    this.updateDateRestrictions();
  }


  ngOnInit() {
    const dateRange = { fDate: moment().startOf('month').format('YYYY-MM-DD'), tDate: moment().format('YYYY-MM-DD'), selectionType: "CustomRange" };
    this.selectedDate = dateRange;

    if (this.isBrowser) {
      this.fetchGridData();
    } else {
      console.log('Running on the server, skipping browser-specific logic.');
    }

    this.setModalSize();
    window.addEventListener('resize', () => this.setModalSize());

    this.gridOptions = {
      context: { componentParent: this },
      onGridReady: (params: any) => {
        this.gridApi = params.api;
        this.gridColumnApi = params.columnApi;
      }
    };

    this.getCompanyList();
    this.getMostRecentData();
    this.getFuntionalityList();
  }

  updateDateRestrictions() {
    const today = new Date();

    if (this.searchOlderThan90Days) {
      // When checkbox is checked - allow older dates (set minDate to a very old date)
      const veryOldDate = new Date(2000, 0, 1); // January 1, 2000 or any old date
      this.minDate = new NgbDate(veryOldDate.getFullYear(), veryOldDate.getMonth() + 1, veryOldDate.getDate());
    } else {
      // When checkbox is unchecked - restrict to last 90 days
      const ninetyDaysAgo = new Date();
      ninetyDaysAgo.setDate(today.getDate() - 90);
      this.minDate = new NgbDate(ninetyDaysAgo.getFullYear(), ninetyDaysAgo.getMonth() + 1, ninetyDaysAgo.getDate());
    }

    this.maxDate = new NgbDate(today.getFullYear(), today.getMonth() + 1, today.getDate());
  }

  onCheckboxChange() {
    this.updateDateRestrictions(); // This now allows old dates if checked
    if (this.searchOlderThan90Days) {
      if (!this.selectedDateTimeRange) {
        const today = moment();
        this.selectedDateTimeRange = {
          fDate: today.format('YYYY-MM-DD'),
          fTime: '00:00:00',
          tDate: today.format('YYYY-MM-DD'),
          tTime: '23:59:59',
          selectionType: 'CustomRange'
        };
      }

    } else {
      this.selectedDateTimeRange = undefined;
    }
  }

  onGridReady(params: any) {
    this.gridApi = params.api;
    this.gridColumnApi = params.columnApi;
    params.api.sizeColumnsToFit();
    window.addEventListener('resize', () => {
      if (this.gridApi) {
        setTimeout(() => this.gridApi.sizeColumnsToFit(), 200);
      }
    });
  }

  setModalSize() {
    const screenWidth = window.innerWidth;
    if (screenWidth > 1600) {
      this.modalSizeClass = 'modal-dialog modal-lg';
    } else if (screenWidth < 768) {
      this.modalSizeClass = 'modal-dialog modal-fullscreen';
    } else {
      this.modalSizeClass = 'modal-dialog';
    }
  }

  toggleCollapse() {
    this.isCollapsed = !this.isCollapsed;
  }

  dateRangeChange(event: any) {
    this.selectedDate = event;
  }

  fetchGridData() {
    this.rowData = [
      { make: 'Tesla', model: 'Model Y', price: 64950, electric: true },
      { make: 'Ford', model: 'F-Series', price: 33850, electric: false },
      { make: 'Toyota', model: 'Corolla', price: 29600, electric: false },
    ];
  }

  dateTimeRangeChange(event: any) {
    this.selectedDateTimeRange = _.cloneDeep(event);
    this.inputDate = moment(this.selectedDateTimeRange.fDate).format('MM-DD-YYYY') + "" + this.selectedDateTimeRange.fTime;
    if (this.selectedDateTimeRange.tTime === "00:00:00") {
      this.inputEndDate = moment(this.selectedDateTimeRange.tDate).format('MM-DD-YYYY') + " 23:59:59";
    } else this.inputEndDate = moment(this.selectedDateTimeRange.tDate).format('MM-DD-YYYY') + " " + this.selectedDateTimeRange.tTime;
  }

  onCompanyChange(companyId: string | number) {
    this.selectedCompanyId = companyId;

    const storeField = this.inputFields.find(f => f.id === 'storeId');
    if (storeField) {
      storeField.value = '';
      storeField.options = [];
    }

    this.getStoreList(companyId);
  }


  getCompanyList() {
    this.spinner.show();
    this.supportdashboardService.getData(`${environment.audit}/api/audit-events/get-all-companies`)
      .subscribe((response) => {
        this.companyList = response;

        if (response.StatusCode == 200 && response?.Data && Array.isArray(response.Data)) {
          this.companies = response.Data.map((item: any) => ({
            label: item.CompanyName,
            value: item.CompanyID
          }));

          const funcField = this.inputFields.find(f => f.id === 'companyId');
          if (funcField) {
            funcField.options = this.companies;
          }
        } else if (response.StatusCode == 400) {
          this.toaster.error(response.message, 'Error');
        } else if (response.StatusCode == 500) {
          this.toaster.error(response.message, 'Error');
        }
        this.spinner.hide();
      });
  }

  getStoreList(companyId: string | number) {
    if (!companyId) return;
    this.spinner.show();

    this.supportdashboardService.getData(`${environment.audit}/api/audit-events/get-storelocations-by-company?company_id=${companyId}`)
      .subscribe((response) => {
        if (response.StatusCode == 200 && response?.Data && Array.isArray(response.Data)) {
          this.stores = response.Data.map((item: any) => ({
            label: item.StoreName,
            value: item.StoreLocationID
          }));

          const storeField = this.inputFields.find(f => f.id === 'storeId');
          if (storeField) {
            storeField.options = this.stores;
          }
        } else if (response.StatusCode == 400) {
          this.toaster.error(response.message, 'Error');
        } else if (response.StatusCode == 500) {
          this.toaster.error(response.message, 'Error');
        }
        this.spinner.hide();
      });
  }

  getMostRecentData() {
    this.spinner.show();

    this.supportdashboardService.getData(`${environment.audit}/api/audit-events/recent`)
      .subscribe({
        next: (response: any) => {
          this.spinner.hide();
          if (response.StatusCode == 200 && response?.events && Array.isArray(response.events)) {
            this.rowData = response.events;
            this.hasData = this.rowData.length > 0;
            this.columnDefs = getAuditColumnDefs(this.rowData)
          }
          else if (response.StatusCode == 400) {
            this.rowData = [];
            this.toaster.error(response.message, 'Error');
          } else if (response.StatusCode == 500) {
            this.rowData = [];
            this.toaster.error(response.message, 'Error');
          } else {
            this.rowData = [];
          }
        },
        error: (err) => {
          console.error("API Error:", err);
          this.spinner.hide();
        }
      });
  }

  getFuntionalityList() {
    this.spinner.show();
    this.supportdashboardService.getData(`${environment.audit}/api/audit-events/get-all-auditfunctionalities`)
      .subscribe({
        next: (response: any) => {
          this.spinner.hide();
          if (response.StatusCode == 200 && response?.Data && Array.isArray(response.Data)) {
            this.functionalities = response.Data.map((item: any) => ({
              label: item.FunctionalityName,
              value: item.FunctionalityID
            }));

            const funcField = this.inputFields.find(f => f.id === 'functionality');
            if (funcField) {
              funcField.options = this.functionalities;
            }
          } else if (response.StatusCode == 400) {
            this.toaster.error(response.message, 'Error');
          } else if (response.StatusCode == 500) {
            this.toaster.error(response.message, 'Error');
          }
        },
        error: (err) => {
          console.error("Error fetching functionalities:", err);
          this.spinner.hide();
        }
      });
  }

  onFuntionalityChange(event: any) {
    const eventTypeField = this.inputFields.find(f => f.id === 'eventType');
    if (eventTypeField) {
      eventTypeField.value = '';
      eventTypeField.options = [];
    }
    this.getEventTypeList(event);
  }

  getEventTypeList(selectedFunctionalityId: any) {
    const selectedFunctionality = this.functionalities.find(f => f.value === selectedFunctionalityId)?.label;
    if (!selectedFunctionality) return;

    this.spinner.show();
    this.supportdashboardService.getData(`${environment.audit}/api/audit-events/get-eventtypenames-by-functionalityname?functionalityname=${selectedFunctionality}`)
      .subscribe({
        next: (response: any) => {
          this.spinner.hide();

          if (response.StatusCode == 200 && response?.events && Array.isArray(response.events)) {
            this.eventTypes = response.events.map((item: any) => ({
              label: item.EventTypeName,
              value: item.EventTypeID
            }));
            const eventTypeField = this.inputFields.find(f => f.id === 'eventType');
            if (eventTypeField) {
              eventTypeField.options = this.eventTypes;
            }
          } else if (response.StatusCode == 400) {
            this.toaster.error(response.message, 'Error');
          } else if (response.StatusCode == 500) {
            this.toaster.error(response.message, 'Error');
          }
        },
        error: (err) => {
          console.error("Error fetching functionalities:", err);
          this.spinner.hide();
        }
      });
  }

  onSearch() {
    const params: any = {
      page_number: 1,
      page_size: 5000,
    };

    let startDateForAPI: string;
    let endDateForAPI: string;

    if (this.selectedDateTimeRange) {
      const fDate = moment(this.selectedDateTimeRange.fDate).format('MM-DD-YYYY');
      const tDate = moment(this.selectedDateTimeRange.tDate).format('MM-DD-YYYY');
      const fTime = this.selectedDateTimeRange.fTime;
      const tTime = this.selectedDateTimeRange.tTime === "00:00:00" ? "23:59:59" : this.selectedDateTimeRange.tTime;

      startDateForAPI = `${fDate} ${fTime}`;
      endDateForAPI = `${tDate} ${tTime}`;
    } else {
      startDateForAPI = moment().format('MM-DD-YYYY') + " 00:00:00";
      endDateForAPI = moment().format('MM-DD-YYYY') + " 23:59:59";
    }
    console.log("startDateForAPI", startDateForAPI)
    console.log("endDateForAPI", endDateForAPI)

    params.from_date = startDateForAPI;
    params.to_date = endDateForAPI;

    this.inputFields.forEach((field) => {
      if (field.value && field.value !== '') {
        switch (field.id) {
          case 'companyId':
            params.company_id = field.value;
            break;
          case 'storeId':
            params.store_id = field.value;
            break;
          case 'user':
            params.user = field.value;
            break;
          case 'functionality':
            const selectedFunctionality = this.functionalities.find(f => f.value === field.value);
            if (selectedFunctionality) {
              params.functionality = selectedFunctionality.label;  // Send the functionality name
            }
            break;
          case 'eventType':
            if (field.value) {
            const selectedEventType = this.eventTypes.find(e => e.value === field.value);
            if (selectedEventType) {
              params.event_type = selectedEventType.label;  // Send the event type name
            }
          }
            break;
          case 'message':
            params.message_pattern = field.value;
            break;
        }
      }
    });

    const query = new URLSearchParams(params).toString();
    const apiUrl = `${environment.audit}/api/audit-events/search?${query}`;
    this.spinner.show();

    this.supportdashboardService.getData(apiUrl).subscribe({
      next: (response: any) => {
        this.spinner.hide();
        if (this.gridApi) {
          this.gridApi.paginationGoToFirstPage();
        }
        if (response.StatusCode === 200 && (response?.events && Array.isArray(response.events))) {
          this.rowData = response.events;
          this.hasData = this.rowData.length > 0;
        } else if (response.StatusCode == 400) {
          this.rowData = response.events;
          this.hasData = this.rowData.length > 0;
          this.toaster.warning(response.message, 'Warning');
        } else if (response.StatusCode == 500) {
          this.toaster.error(response.message, 'Error');
        }
      },
      error: (err) => {
        console.error('Error fetching search results:', err);
        this.spinner.hide();
      },
    });
  }

  onReset() {
    this.inputFields.forEach(f => f.value = '');
    this.searchOlderThan90Days = false;
    this.selectedDateTimeRange = undefined;
    this.selectedDate = undefined;
    setTimeout(() => {
      this.selectedDateTimeRange = null;
    }, 0);

    this.inputDate = moment().format('MM-DD-YYYY');
    this.inputEndDate = moment().format('MM-DD-YYYY');

    this.updateDateRestrictions();
    this.hasData = false;
    this.getMostRecentData();
  }


  showAdditionalDataPopup(additionalData: any) {
    this.selectedAdditionalData = additionalData;
    this.showPopup = true;
  }

  closePopup() {
    this.showPopup = false;
  }

  buildExportUrl(): string {
    const params: any = {
      page_number: 1, // Start with base params for full export
    };
    let hasFilters = false;

    // ✅ Check if custom date range is set
    if (this.selectedDateTimeRange) {
      hasFilters = true;

      const fDate = moment(this.selectedDateTimeRange.fDate).format('MM-DD-YYYY');
      const tDate = moment(this.selectedDateTimeRange.tDate).format('MM-DD-YYYY');
      const fTime = this.selectedDateTimeRange.fTime;
      const tTime = this.selectedDateTimeRange.tTime === "00:00:00" ? "23:59:59" : this.selectedDateTimeRange.tTime;

      params.from_date = `${fDate} ${fTime}`;
      params.to_date = `${tDate} ${tTime}`;
    }

    this.inputFields.forEach((field) => {
      if (field.value && field.value !== '') {
        hasFilters = true;
        switch (field.id) {
          case 'companyId':
            params.company_id = field.value;
            break;
          case 'storeId':
            params.store_location_id = field.value;
            break;
          case 'user':
            params.username = field.value;
            break;
          case 'functionality':
            params.functionality_name = field.value;
            break;
          case 'eventType':
            params.event_type_name = field.value;
            break;
          case 'message':
            params.message_pattern = field.value;
            break;
        }
      }
    });

    if (hasFilters) {
      params.recent = false;
      params.page_size = 5000;
    } else {
      params.recent = true;
      params.page_size = 500;
    }

    const query = new URLSearchParams(params).toString();
    return `/api/audit-events/export?${query}`;
  }

  triggerFileDownload(response: Blob, filename: string) {
    const fileURL = URL.createObjectURL(response);
    const link = document.createElement('a');
    link.href = fileURL;
    link.download = filename; // Set the default filename
    document.body.appendChild(link);
    link.click();
    URL.revokeObjectURL(fileURL);
  }

  onExport() {
    this.gridApi.exportDataAsExcel({
      fileName: 'Audit-records.xlsx',
      sheetName: 'Audit Sheet',
    });
    this.spinner.show();
    const apiUrl = this.buildExportUrl(); // Call the first helper method

    this.supportdashboardService.exportAuditData(apiUrl).subscribe({
      next: (response: HttpResponse<Blob>) => {
        this.spinner.hide();
        console.log(response)
        const blob = response.body;
        const contentType = response.headers.get('Content-Type') || '';
        const contentDisposition = response.headers.get('Content-Disposition') || '';
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
        const filename = filenameMatch ? filenameMatch[1] : 'Audit-export.xlsx';


        if (contentType.includes('text/html')) {
          const reader = new FileReader();
          reader.onload = () => {
            // console.error("HTML response received instead of file", reader.result);
          };
          reader.readAsText(blob);
          return;
        }

        this.triggerFileDownload(blob, filename);
      },
      error: (err) => {
        this.spinner.hide();
        console.error("API Error during export:", err);
      }
    });
  }

  ngOnDestroy() {
    window.removeEventListener('resize', () => this.setModalSize());
  }

}
