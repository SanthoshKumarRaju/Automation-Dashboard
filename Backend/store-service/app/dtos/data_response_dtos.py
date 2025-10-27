from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


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
    
class PaginationResponse(BaseModel):
    statusCode: int
    message: str
    total_count: int
    page: int
    page_size: int
    total_pages: int
    data: List[Dict[str, Any]]