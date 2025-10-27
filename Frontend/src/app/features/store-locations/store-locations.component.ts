import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { AgGridAngular } from 'ag-grid-angular';
import { themeQuartz, iconSetQuartzBold, ColDef } from 'ag-grid-community';
import { SupportdashboardService } from '../../services/supportdashboard.service';
import { ModuleRegistry, Module } from 'ag-grid-community';
import { ExcelExportModule } from 'ag-grid-enterprise';
import {
  Bootstrap_Theme,
  DefaultColDef,
  getStoreColumnDefs,
} from '../../shared/models/gridmodel';
import { environment } from '../../../environments/environment';
import { NgxSpinnerService } from 'ngx-spinner';
@Component({
  selector: 'app-store-locations',
  standalone: true,
  imports: [CommonModule, AgGridAngular],
  templateUrl: './store-locations.component.html',
  styleUrl: './store-locations.component.scss',
})
export class StoreLocationsComponent implements OnInit {
  public total_count: any;
  public inputFields: any;
  public isBrowser: any = false;
  public columnDefs: any[] = [];
  public defaultColDef: any = DefaultColDef;
  public bt_theme: any = Bootstrap_Theme;
  public rowData: any[] = [];
  public gridApi: any;
  public gridColumnApi: any;
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
    ModuleRegistry.registerModules([ExcelExportModule]);

    setTimeout(() => {
      this.isBrowser = true;
    }, 100);
    this.fetch_info();
  }
  onGridReady(params: any) {
    this.gridApi = params.api;
    this.gridColumnApi = params.columnApi;
  }
  onBtnExport() {
    this.gridApi.exportDataAsExcel({
      fileName: 'POS_Report.xlsx',
      sheetName: 'POS Data',
      excelStyles: this.excelStyles,
    });
  }
  fetch_info() {
    this.spinner.show();
    this.apiService
      .getData(`${environment.store}/api/data/store-data`)
      .subscribe((res) => {
        this.rowData = res.data;
        this.columnDefs = getStoreColumnDefs(this.rowData);
        this.total_count = res.total_count;
        this.spinner.hide();
      });
  }
  refreshData() {
   this.fetch_info()
  }
}
