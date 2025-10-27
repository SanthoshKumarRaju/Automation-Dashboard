from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any

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