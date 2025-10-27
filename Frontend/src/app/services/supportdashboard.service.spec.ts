import { TestBed } from '@angular/core/testing';

import { SupportdashboardService } from './supportdashboard.service';

describe('SupportdashboardService', () => {
  let service: SupportdashboardService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SupportdashboardService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
