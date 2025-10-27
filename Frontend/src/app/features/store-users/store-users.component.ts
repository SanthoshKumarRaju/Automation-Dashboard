import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { AgGridAngular } from 'ag-grid-angular';
import {
  themeQuartz,
  iconSetQuartzBold,
  ModuleRegistry,
  ColDef,
} from 'ag-grid-community';
import { SetFilterModule } from 'ag-grid-enterprise';
import { SupportdashboardService } from '../../services/supportdashboard.service';
import {
  Bootstrap_Theme,
  DefaultColDef,
  UserGridColumnDefs,
} from '../../shared/models/gridmodel';
import { environment } from '../../../environments/environment';
import { NgxSpinnerService } from 'ngx-spinner';
ModuleRegistry.registerModules([SetFilterModule]);
@Component({
  selector: 'app-store-users',
  standalone: true,
  imports: [CommonModule, AgGridAngular],
  templateUrl: './store-users.component.html',
  styleUrl: './store-users.component.scss',
})
export class StoreUsersComponent implements OnInit {
  public inputFields: any;
  public isBrowser: any = false;
  public total_count: any;
  public unique_user: any;
  public rowData: any[] = [];
  public gridApi: any;
  public gridColumnApi: any;
  public columnDefs: ColDef[] = UserGridColumnDefs;
  public defaultColDef: any = DefaultColDef;
  public bt_theme: any = Bootstrap_Theme;
  public excelStyles = [
    {
      id: 'rightAlign', // style ID
      alignment: { horizontal: 'Right' }, // right alignment
    },
    {
      id: 'headerStyle',
      font: { bold: true, size: 14 },
      alignment: { horizontal: 'Center' }, // header centered
    },
  ];
  constructor(
    private apiService: SupportdashboardService,
    private spinner: NgxSpinnerService
  ) {}

  ngOnInit(): void {
    setTimeout(() => {
      this.isBrowser = true;
    }, 100);
    this.fetch_info();
  }

  onGridReady(params: any) {
    this.gridApi = params.api;
    this.gridColumnApi = params.columnApi;
  }
  fetch_info() {
    this.spinner.show();
    this.apiService
      .getData(`${environment.store}/api/data/user-data`)
      .subscribe((res) => {
        this.rowData = res.data;
        this.total_count = res.total_count;
        this.spinner.hide();
      });
  }
  refreshData() {
    this.fetch_info();
  }
  onBtnExport() {
    this.gridApi.exportDataAsExcel({
      fileName: 'storeUsers_Report.xlsx',
      sheetName: 'POS Data',
      excelStyles: this.excelStyles,
    });
  }
}

// to use myTheme in an application, pass it to the theme grid option
const myTheme = themeQuartz.withPart(iconSetQuartzBold).withParams({
  browserColorScheme: 'inherit',
  /* Header styling like Bootstrap */
  headerBackgroundColor: '#f8f9fa', // Bootstrap light gray header
  headerTextColor: '#212529', // Bootstrap dark text
  headerFontFamily: [
    '-apple-system',
    'BlinkMacSystemFont',
    'Segoe UI',
    'Roboto',
    'Oxygen-Sans',
    'Ubuntu',
    'Cantarell',
    'Helvetica Neue',
    'sans-serif',
  ],
  headerFontSize: 14,
  headerFontWeight: 500,
  headerVerticalPaddingScale: 1.2,

  // rowBackgroundColorEven: "#ffffff",
  // rowBackgroundColorOdd: "#f8f9fa",
  // rowHoverBackgroundColor: "#e9ecef",
  // rowTextColor: "#212529",
  // rowFontSize: 14,

  /* Borders */
  sidePanelBorder: true,
  wrapperBorder: true,
  borderColor: '#dee2e6', // Bootstrap table border

  /* Icons */
  iconSize: 14,
});
