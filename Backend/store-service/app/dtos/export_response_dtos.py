from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class LoginResponse(BaseModel):
    statusCode: int
    message: str
    username: str
    access_token: str
    timestamp: datetime

class StoreDataResponse(BaseModel):
    StoreLocationID: int
    POSSystemCD: Optional[str]
    CompanyID: Optional[int]
    StoreName: Optional[str]
    ZIPCode: Optional[str]
    IsPCLess: Optional[bool]
    MNSPID: Optional[str]
    PaymentSystemsProductName: Optional[str]
    SiteIP: Optional[str]
    Scandata: Optional[str]
    RCN: Optional[str]
    LatestEndDateTime: Optional[str]

class UserDataResponse(BaseModel):
    CompanyID: Optional[int]
    CompanyName: Optional[str]
    StoreID: Optional[int]
    StoreName: Optional[str]
    UserName: Optional[str]
    UserMail: Optional[str]
    UserRole: Optional[str]
    LastLogon: Optional[str]

class FilterOptionsResponsedata(BaseModel):
    POSSystemCD: List[str]
    MNSPID: List[str]
    PaymentSystemsProductName: List[str]
    
class FilterOptionsResponse(BaseModel):
    statusCode: int
    message: str
    data: FilterOptionsResponsedata

class UserRolesResponse(BaseModel):
    statusCode: int
    message: str
    user_roles: List[str]

class HealthCheckResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
    version: str = "1.0.0"

class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None
    timestamp: datetime

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None
    code: Optional[int] = None
    timestamp: datetime
    
class PaginationResponse(BaseModel):
    statusCode: int
    message: str
    total_count: int
    page: int
    page_size: int
    total_pages: int
    data: List[Dict[str, Any]]