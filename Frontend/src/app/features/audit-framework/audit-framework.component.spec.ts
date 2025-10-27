import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AuditFrameworkComponent } from './audit-framework.component';

describe('AuditFrameworkComponent', () => {
  let component: AuditFrameworkComponent;
  let fixture: ComponentFixture<AuditFrameworkComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AuditFrameworkComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(AuditFrameworkComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
