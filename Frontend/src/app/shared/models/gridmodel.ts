// user-grid.model.ts
import { ColDef, iconSetQuartzBold, themeQuartz } from 'ag-grid-community';

export const UserGridColumnDefs: ColDef[] = [
  {
    headerName: 'S.No',
    field: 'SerialNumber',
    width: 80,
    sortable: true,
    filter: false,
  },
  {
    headerName: 'CompanyID',
    field: 'CompanyID',
    filter: 'agSetColumnFilter',
    filterParams: {
      values: ['Tech Solutions', 'Green Mart', 'Blue Ocean Corp'],
    },
  },
  {
    headerName: 'Company Name',
    field: 'CompanyName',
    filter: 'agTextColumnFilter',
  },
  {
    headerName: 'Store ID',
    field: 'StoreID',
    filter: 'agTextColumnFilter',
  },
  {
    headerName: 'Store Name',
    field: 'StoreName',
    filter: 'agTextColumnFilter',
  },
  {
    headerName: 'User Name',
    field: 'UserName',
    filter: 'agTextColumnFilter',
  },
  {
    headerName: 'User EmailID',
    field: 'UserMail',
    filter: 'agTextColumnFilter',
  },
  {
    headerName: 'User Role',
    field: 'UserRole',
    filter: 'agSetColumnFilter',
    filterParams: {
      values: ['Admin', 'Manager', 'User'],
    },
  },
  {
    headerName: 'Lastlogon',
    field: 'LastLogon',
    filter: 'agDateColumnFilter',
  },
];

// Default column definition
export const DefaultColDef: ColDef = {
  sortable: true,
  filter: true,
  resizable: true,
  autoHeight: true,
};

export const Bootstrap_Theme = themeQuartz
  .withPart(iconSetQuartzBold)
  .withParams({
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

    /* Borders */
    sidePanelBorder: true,
    wrapperBorder: true,
    borderColor: '#dee2e6', // Bootstrap table border

    /* Icons */
    iconSize: 14,
  });
export function getStoreColumnDefs(rowData: any[]): ColDef[] {
  return [
    {
      headerName: 'S.No',
      width: 80,
      sortable: false,
      filter: false,
      valueGetter: (params: any) => params.node.rowIndex + 1,
    },
    {
      headerName: 'StoreLocationID',
      field: 'StoreLocationID',
      filter: 'agTextColumnFilter',
      cellRenderer: (params: any) => `<a href="#">${params.value}</a>`,
    },
    {
      headerName: 'POSSystemCD',
      field: 'POSSystemCD',
      filter: 'agSetColumnFilter',
      filterParams: {
        values: (params: any) => {
          const uniqueValues = Array.from(
            new Set(rowData.map((item: any) => item.POSSystemCD))
          );
          params.success(uniqueValues);
        },
      },
    },
    {
      headerName: 'CompanyID',
      field: 'CompanyID',
      filter: 'agTextColumnFilter',
    },
    {
      headerName: 'StoreName',
      field: 'StoreName',
      filter: 'agTextColumnFilter',
    },
    { headerName: 'ZIPCode', field: 'ZIPCode', filter: 'agTextColumnFilter' },
    { headerName: 'IsPCLess', field: 'IsPCLess', filter: 'agSetColumnFilter' },
    {
      headerName: 'MNSPID',
      field: 'MNSPID',
      filter: 'agSetColumnFilter',
      filterParams: {
        values: (params: any) => {
          const uniqueValues = Array.from(
            new Set(rowData.map((item) => item.MNSPID))
          );
          params.success(uniqueValues);
        },
      },
    },
    {
      headerName: 'FuelBrand',
      field: 'FuelBrand',
      filter: 'agSetColumnFilter',
      filterParams: {
        values: (params: any) => {
          const uniqueValues = Array.from(
            new Set(rowData.map((item) => item.FuelBrand))
          );
          params.success(uniqueValues);
        },
      },
    },
    { headerName: 'SiteIP', field: 'SiteIP', filter: 'agTextColumnFilter' },
    { headerName: 'Scandata', field: 'Scandata', filter: 'agTextColumnFilter' },
    { headerName: 'RCN', field: 'RCN', filter: 'agTextColumnFilter' },
    {
      headerName: 'LastDayClose',
      field: 'LastDayClose',
      filter: 'agDateColumnFilter',
    },
  ];
}

export function getAuditColumnDefs(rowData: any[]): ColDef[] {
  const screenWidth = window.innerWidth;
  const isSmall = screenWidth < 768;
  const isMedium = screenWidth >= 1400 && screenWidth <= 1600;

  const widthConfig = {
    small: 110,
    medium: 250,
    large: 300,
  };

  const colWidth = isSmall
    ? widthConfig.small
    : isMedium
      ? widthConfig.medium
      : widthConfig.large;

  return [
    {
      headerName: 'Date Time',
      field: 'EventTimestamp',
      width: colWidth - 80,
      wrapText: true,
      cellStyle: {
        display: 'flex',
        alignItems: 'center', // vertical centering
        whiteSpace: 'normal', // allows text to wrap
        borderRight: '1px solid #aaabacff',
      },
      headerClass: 'justify-content-center',

      cellRenderer: (params: any) =>
        `<a class="date-link" style="text-decoration:none; color:#007bff; cursor:pointer;">${params.value}</a>`,
      onCellClicked: (params: any) => {
        // Prevent the <a> default click behavior
        if (params.event) {
          params.event.preventDefault();
          params.event.stopPropagation();
        }
        if (params && params.data && params.data.AdditionalData) {
          const latest = params.data;
          params.context.componentParent.showAdditionalDataPopup(latest);
        }
      },
    },
    {
      headerName: 'Functionality',
      field: 'Functionality',
      width: colWidth - 80,
      wrapText: true,
      cellStyle: {
        display: 'flex',
        alignItems: 'center', // vertical centering
        whiteSpace: 'normal', // allows text to wrap
        borderRight: '1px solid #aaabacff',
      },
      headerClass: 'justify-content-center',

    },
    {
      headerName: 'Event Type',
      field: 'EventType',
      width: colWidth - 50,
      wrapText: true,
      cellStyle: {
        display: 'flex',
        alignItems: 'center', // vertical centering
        whiteSpace: 'normal', // allows text to wrap
        borderRight: '1px solid #aaabacff',
      },
      headerClass: 'justify-content-center',

    },
    {
      headerName: 'User',
      field: 'UserName',
      width: colWidth - 120,
      wrapText: true,
      cellStyle: {
        display: 'flex',
        alignItems: 'center', // vertical centering
        whiteSpace: 'normal', // allows text to wrap
        borderRight: '1px solid #aaabacff',
      },
      headerClass: 'justify-content-center',

    },
    {
      headerName: 'Store',
      field: 'StoreName',
      width: colWidth - 80,
      wrapText: true,
      cellStyle: {
        display: 'flex',
        alignItems: 'center', // vertical centering
        whiteSpace: 'normal', // allows text to wrap
        borderRight: '1px solid #aaabacff',
      },
      headerClass: 'justify-content-center',

    },
    {
      headerName: 'Message', field: 'Message',
      wrapText: true,
      flex: 1,
      cellStyle: {
        display: 'flex',
        alignItems: 'center', // vertical centering
        whiteSpace: 'normal', // allows text to wrap
        borderRight: '1px solid #aaabacff',
      },
      headerClass: 'justify-content-center',

    },
  ];
}
