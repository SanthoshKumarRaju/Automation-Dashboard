from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_serializer
import pytz

class AuditEventCreate(BaseModel):
    event_timestamp: datetime
    functionality: str
    event_type: str
    store_id: Optional[int] = None
    company_id: Optional[int] = None
    user: str
    message: str
    status: str = "Success"
    additional_data: Optional[Dict[str, Any]] = None

    @field_serializer("event_timestamp")
    def format_event_timestamp(self, value: datetime) -> str:
        # Ensure timestamp is in Central Time for consistency
        central_tz = pytz.timezone("America/Chicago")
        if value.tzinfo is None:
            value = pytz.UTC.localize(value)
        ct_timestamp = value.astimezone(central_tz)
        return ct_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    

class AuditEventSearch(BaseModel):
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    functionality: Optional[str] = None
    store_id: Optional[int] = None
    user: Optional[str] = None
    message_pattern: Optional[str] = None
    page_number: int = Field(1, ge=1)
    page_size: int = Field(500, ge=1, le=5000)
    

class AuditEventResponse(BaseModel):
    Id: int
    EventTimestamp: str
    Functionality: str
    EventType: str
    StoreLocationID: Optional[int] = None
    StoreName: Optional[str] = None
    CompanyId: int
    CompanyName: Optional[str] = None
    UserName: str
    Message: str
    Status: str
    AdditionalData: Optional[Dict[str, Any]]
    
    # # Custom serializer for event_timestamp
    # @field_serializer("EventTimestamp")
    # def format_event_timestamp(self, value: datetime) -> str:
    #     # Ensure timestamp is in Central Time for consistency
    #     central_tz = pytz.timezone("America/Chicago")
    #     if value.tzinfo is None:
    #         value = pytz.UTC.localize(value)
    #     ct_timestamp = value.astimezone(central_tz)
    #     return ct_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    

class SearchResponse(BaseModel):
    StatusCode: int
    message: str
    count: int
    # current_page: int
    # total_pages: int
    # page_size: int
    events: List[AuditEventResponse]
    
    
class RecentAuditEventsResponse(BaseModel):
    StatusCode: int
    message: str
    count: int
    events: List[AuditEventResponse]


class AuditEvent(BaseModel):
    Id: int
    EventTimestamp: datetime
    Functionality: str
    EventType: str
    StoreLocationID: Optional[int]
    CompanyId: int
    UserName: str
    Message: str
    Status: str
    AdditionalData: Optional[Any]


class RecentAuditEventsResponse(BaseModel):
    events: List[AuditEvent]