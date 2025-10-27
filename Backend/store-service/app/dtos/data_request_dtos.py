from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any

class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator('username')
    def username_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Username cannot be empty')
        return v.strip()

    @field_validator('password')
    def password_not_empty(cls, v):
        if not v:
            raise ValueError('Password cannot be empty')
        return v

class FilterRequest(BaseModel):
    filters: Optional[Dict[str, Any]] = {}
    sort_column: Optional[str] = None
    sort_order: Optional[str] = 'desc'
    page: Optional[int] = 1
    page_size: Optional[int] = 100

    @field_validator('sort_order')
    def validate_sort_order(cls, v):
        if v and v.lower() not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v.lower()

    @field_validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be at least 1')
        return v

    @field_validator('page_size')
    def validate_page_size(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('Page size must be between 1 and 1000')
        return v

class ExportRequest(BaseModel):
    data: List[Dict[str, Any]]
    export_type: Optional[str] = 'excel'

    @field_validator('data')
    def validate_data(cls, v):
        if not v:
            raise ValueError('Data cannot be empty')
        return v

    @field_validator('export_type')
    def validate_export_type(cls, v):
        if v not in ['excel']:
            raise ValueError('Export type must be "excel"')
        return v

class DataRefreshRequest(BaseModel):
    data_type: str  # 'store' or 'user'

    @field_validator('data_type')
    def validate_data_type(cls, v):
        if v not in ['store', 'user', 'all']:
            raise ValueError('Data type must be "store", "user", or "all"')
        return v

class PaginationResponse(BaseModel):
    data: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    total_pages: int