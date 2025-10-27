import { HttpInterceptorFn } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export const apiKeyInterceptor: HttpInterceptorFn = (req, next) => {
  const apiKey = environment.api_key;
  const clonedReq = req.clone({
    setHeaders: {
      'CSIQ-API-KEY': apiKey,
      'accept': 'application/json'
    }
  });

  return next(clonedReq);
};
