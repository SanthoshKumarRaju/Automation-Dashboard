from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from app.dtos.audit_req_res import AuditEventCreate, SearchResponse
from app.services import audit_service
from app.dependencies.db_session_dependency import PostgresDBSession , SqlServerDBSession
from fastapi.responses import StreamingResponse
import io
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix='/api')

# This is the healthcheck endpoint.
@router.get("/healthcheck", tags=["Health Check"])
async def healthcheck():
    return {
        "status": "healthy",
        "message": "python audit service is running"
    }

# This endpoint is used to create the audit events.
@router.post("/audit-events/create", response_model=dict, status_code=201, tags=["Audit Events"])
async def create_audit_event(request: AuditEventCreate, db_session: PostgresDBSession):
    """Create a new audit event --> This endpoint only uses API-KEY validation"""
    return await audit_service.insert_audit_event(event=request, session=db_session)


# This endpoint is used to search the recent 500 events by default.
@router.get("/audit-events/recent", tags=["Audit Events"])
async def get_recent_audit_events(db_session: PostgresDBSession, sqlserver_session: SqlServerDBSession):
    """Get most recent audit events (up to 500)"""
    return await audit_service.get_recent_events(session=db_session, sqlserver_session=sqlserver_session)


# This endpoint is used to get the eventtypenames based on functionalityname.
@router.get("/audit-events/get-eventtypenames-by-functionalityname", tags=["Audit Events"])
async def get_eventtypenames_by_functionalityname(functionalityname: str, db_session: PostgresDBSession):
    """Get event type names by functionality name"""
    return await audit_service.get_eventtypenames_by_functionalityname(functionalityname, session=db_session)


# This endpoint is used to search the audit events based on search criteria.
@router.get("/audit-events/search", response_model=SearchResponse, tags=["Audit Events"])
async def search_audit_events(
    db_session: PostgresDBSession,
    sqlserver_session: SqlServerDBSession,
    from_date: Optional[str] = None,  
    to_date: Optional[str] = None,   
    functionality: Optional[str] = None,
    event_type: Optional[str] = None,
    company_id: Optional[int] = None,
    store_id: Optional[int] = None,
    user: Optional[str] = None,
    message_pattern: Optional[str] = None,
    page_number: int = Query(1, ge=1),
    page_size: int = Query(500, ge=1, le=5000)
    
):
    """Search audit events using search criteria"""
    return await audit_service.search_audit_events(
        from_date=from_date,
        to_date=to_date,
        functionality=functionality,
        event_type=event_type,
        store_id=store_id,
        company_id=company_id,
        user=user,
        message_pattern=message_pattern,
        page_number=page_number,
        page_size=page_size,
        session=db_session,
        sqlserver_session=sqlserver_session
    )


# This endpoint is used to export the audit event data to an Excel sheet.
@router.get("/audit-events/export", tags=["Audit Events"])
async def export_audit_events_to_excel(
    db_session: PostgresDBSession,
    sqlserver_session: SqlServerDBSession,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    functionality: Optional[str] = None,
    event_type: Optional[str] = None,
    company_id: Optional[int] = None,
    store_id: Optional[int] = None,
    user: Optional[str] = None,
    message_pattern: Optional[str] = None,
    page_number: int = Query(1, ge=1),
    page_size: int = Query(500, ge=1, le=5000),
    recent: bool = Query(
        False,
        description="If true, exports the most recent 500 events instead of search results."
    ),
):
    """
    Export audit events to an Excel file.

    - If `recent=True`, exports the latest 500 audit events.
    - Otherwise, exports events matching the given search criteria.
    """
    try:
        if recent:
            logger.info("Exporting the most recent 500 audit events to Excel...")
            search_result = await audit_service.get_recent_events(session=db_session, sqlserver_session=sqlserver_session)
        else:
            logger.info("Exporting filtered audit event search results to Excel...")
            search_result = await audit_service.search_audit_events(
                from_date=from_date,
                to_date=to_date,
                functionality=functionality,
                event_type=event_type,
                store_id=store_id,
                company_id=company_id,
                user=user,
                message_pattern=message_pattern,
                page_number=page_number,
                page_size=page_size,
                session=db_session,
                sqlserver_session=sqlserver_session
            )

        # Generate Excel file
        excel_file = await audit_service.export_audit_events_to_excel(search_result, sqlserver_session)

        # Create a timestamped filename
        timestamp = datetime.now().strftime("%m%d%Y_%H%M%S")
        filename = (
            f"audit_events_recent_{timestamp}.xlsx"
            if recent
            else f"audit_events_search_{timestamp}.xlsx"
        )

        logger.info(f"Audit events exported successfully: {filename}")

        # Return the Excel file as a download response
        return StreamingResponse(
            io.BytesIO(excel_file),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.exception("Error exporting audit events to Excel:")
        raise HTTPException(status_code=500, detail="Something went wrong")

    
# This endpoint is used to get all the auditfunctionalities.
@router.get("/audit-events/get-all-auditfunctionalities", tags=["Audit Events"])
async def get_all_auditfunctionalities(db_session: PostgresDBSession):
    """Get all audit functionalities"""
    return await audit_service.get_all_auditfunctionalities(session=db_session)


# This endpoint is used to get all company details.
@router.get("/audit-events/get-all-companies", tags=["Company"])
async def get_all_companies(db_session: SqlServerDBSession):
    """Get all companies"""
    return await audit_service.get_all_companies(session=db_session)


# This endpoint is used to get all store locations for a given company.
@router.get("/audit-events/get-storelocations-by-company", tags=["Store Location"])
async def get_store_locations_by_company(company_id: int, db_session: SqlServerDBSession):
    """Get store locations by company ID"""
    return await audit_service.get_store_locations_by_company(company_id=company_id, session=db_session)