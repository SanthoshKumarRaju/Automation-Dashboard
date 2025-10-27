// src/app/core/interceptor/auth.interceptor.ts
import { HttpInterceptorFn, HttpRequest, HttpHandler } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const AuthInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router); // inject Router
  const token = localStorage.getItem('session_id');

  let authReq = req;
  if (token) {
    authReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  return next(authReq).pipe(
    catchError(err => {
      if (err.status == 401||err.status == 0) {
        localStorage.clear()
        router.navigate(['/login']);
      }
      return throwError(() => err);
    })
  );
};
