import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { catchError, map, Observable, throwError } from 'rxjs';
import { HttpClient, HttpHeaders, HttpParams, HttpResponse } from '@angular/common/http';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root',
})
export class SupportdashboardService {
  private auditUrl = environment.audit;
  private baseUrl = environment.baseurl;
  private sessionId = localStorage.getItem('session_id');

  key: any;
  // private sessionId = localStorage.getItem('session_id');

  constructor(private http: HttpClient, private router: Router) { }
  getData(endpoint: string): Observable<any> {
    return this.http.get(`${this.baseUrl}${endpoint}`, {});
  }
  login_service(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}${environment.login}/login`, data, {});
  }
  logout_service() {
    return this.http.get(`${this.baseUrl}/logout`)
  }

  getAuditData(endpoint: string): Observable<any> {
    const url = `${this.auditUrl}${endpoint}`;
    return this.http.get(url);
  }

  // exportAuditData(endpoint: string): Observable<HttpResponse<Blob>> {
  //   const fullUrl = this.auditUrl + endpoint;
  //   return this.http.get(fullUrl, {
  //     responseType: 'blob',
  //     observe: 'response'
  //   });
  // }

  exportAuditData(endpoint: string): Observable<HttpResponse<Blob>> {
    const fullUrl = this.auditUrl + endpoint;

    const token = localStorage.getItem('session_id'); // Or whatever your token key is
    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    return this.http.get(fullUrl, {
      headers,
      responseType: 'blob',
      observe: 'response'
    });
  }
}
