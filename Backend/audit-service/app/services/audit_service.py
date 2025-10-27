import json
from datetime import datetime
import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.configurations import dbconfig as config
from app.utils.logger import get_logger
from sqlalchemy import text, select
from app.dtos.audit_req_res import AuditEventCreate, AuditEventResponse
from typing import Optional
import pandas as pd
from app.db_models import audit_event_models, auditeventarchival_models, auditeventtype_models, auditfunctionality_models,\
    company_models, store_location_models
import io
from app.dependencies.db_session_dependency import SqlServerDBSession
from openpyxl.styles import Font 

settings = config.Settings()
logger = get_logger(__name__)


# This function is used to fetch the storelocationname from sqlserver based on storelocationid
def get_store_name(store_id: int, session) -> str | None:
    """
    Fetch StoreName from SQL Server using a regular (sync) session.
    """
    # If storelocationid is None returning None
    if store_id is None:
        return None
        
    try:
        logger.info(f"Fetching storeName for storelocationid:{store_id}")
        row = session.query(store_location_models.StoreLocation.StoreLocationID, store_location_models.StoreLocation.StoreName)\
                     .filter(store_location_models.StoreLocation.StoreLocationID == store_id)\
                     .first()
        if row:
            logger.debug(f"StoreName: {row.StoreName} for storelocationid:{store_id}")
            return row.StoreName
        return None
    except Exception as e:
        logger.exception(f"Error fetching StoreName for StoreLocationID={store_id}: {e}")
        return None
    
# This function is used to fetch the companyname from sqlserver based on companyid
def get_company_name(company_id: int, session) -> str | None:
    """
    Fetch CompanyName from SQL Server using a regular (sync) session.
    """
    if company_id is None:
        return None
    try:
        logger.info(f"Fetching CompanyName for companyid:{company_id}")
        row = session.query(company_models.Company.CompanyID, company_models.Company.CompanyName)\
                     .filter(company_models.Company.CompanyID == company_id)\
                     .first()
        if row:
            logger.debug(f"CompanyName: {row.CompanyName} for companyid:{company_id}")
            return row.CompanyName
        return None
    except Exception as e:
        logger.exception(f"Error fetching CompanyName for companyid={company_id}: {e}")
        return None


# This function is used to insert audit events.
async def insert_audit_event(event: AuditEventCreate, session: AsyncSession):
    """Insert new audit event using SQLAlchemy ORM model"""
    try:
        logger.debug(f"Request parameters: functionality='{event.functionality}', event_type='{event.event_type}', user='{event.user}', message='{event.message}', "
                     f"event_timestamp={event.event_timestamp} (UTC), store_id={event.store_id}, company_id={event.company_id}, status='{event.status}', additional_data={event.additional_data}")
        status_value = event.status if event.status else "Success"

        # Convert event_timestamp to Central Time and make it timezone-naive
        central_tz = pytz.timezone("America/Chicago")
        ct_timestamp = event.event_timestamp.astimezone(central_tz)
        naive_timestamp = ct_timestamp.replace(tzinfo=None, microsecond=0)

        # Lookup functionality ID
        func_id = await session.scalar(
            select(auditfunctionality_models.AuditFunctionality.functionalityid).where(
                auditfunctionality_models.AuditFunctionality.functionalityname == event.functionality
            )
        )
        logger.debug(f"FunctionalityID lookup for '{event.functionality}': {func_id}")
        if not func_id:
            logger.warning(f"Unknown functionalityname found: {event.functionality}")
            return {
                "StatusCode": 400,
                "message": f"Unknown functionalityname found: {event.functionality}"
            }

        # Lookup event type ID
        event_type_id = await session.scalar(
            select(auditeventtype_models.AuditEventType.eventtypeid).where(
                auditeventtype_models.AuditEventType.eventtypename == event.event_type
            )
        )
        logger.debug(f"EventTypeID lookup for '{event.event_type}': {event_type_id}")
        if not event_type_id:
            logger.warning(f"Unknown eventtypename found: {event.event_type}")
            return {
                "StatusCode": 400,
                "message": f"Unknown eventtypename found: {event.event_type}"
            }

        # Create AuditEvent ORM object (mapped column names corrected)
        audit_event = audit_event_models.AuditEvent(
            eventtimestamp=naive_timestamp,          # EventTimestamp
            functionalityid=func_id,                # FunctionalityId
            eventtypeid=event_type_id,              # EventTypeId
            storelocationid=event.store_id,         # StoreLocationID
            companyid=event.company_id,             # CompanyId
            username=event.user,                    # UserName
            message=event.message,                  # Message
            status=status_value,                    # Status
            additionaldata=event.additional_data if event.additional_data else None  # AdditionalData
        )

        # Add and commit
        session.add(audit_event)
        await session.commit()
        # await session.refresh(audit_event)  # get generated Id

        logger.info(f"Audit event inserted successfully with ID={audit_event.id}, Timestamp={audit_event.eventtimestamp}")

        return {
            "StatusCode": 201,
            "message": "Audit event created successfully"
        }

    except Exception as e:
        await session.rollback()
        logger.exception(f"Exception during audit event insertion:")  # This will log full traceback
        raise HTTPException(status_code=500, detail=f"Something went wrong")


# This function is used to search the audit events based on request parameters
async def search_audit_events(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    functionality: Optional[str] = None,
    event_type: Optional[str] = None,
    store_id: Optional[int] = None,
    user: Optional[str] = None,
    message_pattern: Optional[str] = None,
    page_number: int = 1,
    page_size: int = 500,
    company_id: Optional[int] = None,
    session: AsyncSession = None,           # Postgres session
    sqlserver_session=None                  # SQL Server session (sync)
):
    """Execute the GetAuditEvents_Func stored function and enrich with StoreName"""
    try:
        logger.debug(
            "Searching audit events from_date=%s, to_date=%s, functionality=%s, eventtype=%s, "
            "store_id=%s, user=%s, message_pattern=%s, page_number=%s, page_size=%s, company_id=%s",
            from_date, to_date, functionality, event_type,
            store_id, user, message_pattern,
            page_number, page_size, company_id
        )

        # Call the stored function to search audit events
        stored_function = text("""
            SELECT * FROM GetAuditEvents_Func(
                :from_date,
                :to_date,
                :functionality,
                :eventtype,
                :store_id,
                :user,
                :message_pattern,
                :company_id
            )
        """)

        params = {
            "from_date": from_date,
            "to_date": to_date,
            "functionality": functionality,
            "eventtype": event_type,
            "store_id": store_id,
            "user": user,
            "message_pattern": message_pattern,
            "company_id": company_id
        }

        result = await session.execute(stored_function, params)
        results = result.mappings().all()
        total_count = len(results)
        logger.info(f"Search completed successfully. Total rows fetched: {total_count}")

        if not results:
            return {
                "StatusCode": 200,
                "message": "No audit events found",
                "count": 0,
                "current_page": page_number,
                "total_pages": 0,
                "page_size": page_size,
                "events": []
            }

        # Manual pagination
        start = (page_number - 1) * page_size
        end = start + page_size
        paged_results = results[start:end]

        # Cache for already fetched StoreNames (only for valid store IDs)
        store_cache = {}
        
        company_cache = {}  # cache to avoid repeated SQL Server lookups

        # Format timestamp, map rows, and fetch StoreName from SQL Server
        events = []
        for row in paged_results:
            ts = row["eventtimestamp"]
            formatted_ts = ts.strftime("%m-%d-%Y %H:%M:%S") if ts else None

            store_location_id = row["storelocationid"]
            company_id = row["companyid"]

            # Handle null store_location_id
            store_name = None
            if store_location_id is not None:
                # Fetch StoreName using cache only for valid store IDs
                if store_location_id in store_cache:
                    store_name = store_cache[store_location_id]
                else:
                    store_name = get_store_name(store_location_id, sqlserver_session)
                    store_cache[store_location_id] = store_name
            else:
                logger.debug("storelocationid is None, skipping StoreName...")
                
            # Fetch CompanyName with caching
            if company_id in company_cache:
                company_name = company_cache[company_id]
            else:
                company_name = get_company_name(company_id, sqlserver_session)
                company_cache[company_id] = company_name

            events.append({
                "Id": row["id"],
                "EventTimestamp": formatted_ts,
                "Functionality": row["functionality"],
                "EventType": row["eventtype"],
                "StoreLocationID": store_location_id,
                "StoreName": store_name,  # This will be None when store_location_id is None
                "CompanyId": row["companyid"],
                "CompanyName": company_name,
                "UserName": row["username"],
                "Message": row["message"],
                "Status": row["status"],
                "AdditionalData": row["additionaldata"],
            })

        total_pages = (total_count + page_size - 1) // page_size

        # Check if count exceeds 5000
        if total_count > 5000:
            warning_message = "Search may return more than 5000 rows. Please modify search criteria."
            logger.warning(warning_message)
            return {
                "StatusCode": 400,
                "message": warning_message,
                "count": len(events),
                "current_page": page_number,
                "total_pages": total_pages,
                "page_size": page_size,
                "events": events
            }

        # Return paginated response
        return {
            "StatusCode": 200,
            "message": "Search completed successfully",
            "count": len(events),
            "current_page": page_number,
            "total_pages": total_pages,
            "page_size": page_size,
            "events": events
        }

    except Exception as e:
        logger.exception("Exception during audit events search:")
        raise HTTPException(status_code=500, detail="Something went wrong")
    

# This function is used to fetch recent 500 records
async def get_recent_events(
    session: AsyncSession,  # Postgres session for audit events
    sqlserver_session: SqlServerDBSession  # Sync SQL Server session for store details
) -> dict:
    """
    Fetch the 500 most recent audit events from Postgres
    and enrich with StoreName from SQL Server.
    Implements caching for repeated StoreLocationIDs.
    """
    try:
        logger.info("Fetching the most recent 500 audit events...")
        query = text("SELECT * FROM GetLatestAuditEvents()")
        result = await session.execute(query)
        rows = result.mappings().all()

        if not rows:
            return {"StatusCode": 200, "message": "Data not found", "count": 0, "events": []}

        events = []
        store_cache = {}  # key: StoreLocationID, value: StoreName
        company_cache = {}  # cache to avoid repeated SQL Server lookups

        for row in rows:
            event_timestamp = row["eventtimestamp"]
            formatted_timestamp = (
                event_timestamp.strftime("%m-%d-%Y %H:%M:%S") if event_timestamp else None
            )

            store_id = row["storelocationid"]
            company_id = row["companyid"]

            # Fetch store name from cache if exists, else from SQL Server
            if store_id in store_cache:
                store_name = store_cache[store_id]
            else:
                store_name = get_store_name(store_id, sqlserver_session)
                store_cache[store_id] = store_name  # save to cache
                
            # Fetch CompanyName with caching
            if company_id in company_cache:
                company_name = company_cache[company_id]
            else:
                company_name = get_company_name(company_id, sqlserver_session)
                company_cache[company_id] = company_name

            events.append({
                "Id": row["id"],
                "EventTimestamp": formatted_timestamp,
                "Functionality": row["functionality"],
                "EventType": row["eventtype"],
                "StoreLocationID": store_id,
                "StoreName": store_name,
                "CompanyId": row["companyid"],
                "CompanyName": company_name,
                "UserName": row["username"],
                "Message": row["message"],
                "Status": row["status"],
                "AdditionalData": row["additionaldata"],
            })

        return {
            "StatusCode": 200, 
            "message": "Data fetched successfully", 
            "count": len(events), 
            "events": events
        }

    except Exception as e:
        logger.exception("Exception during fetch recent 500 records:")
        raise HTTPException(status_code=500, detail="Something went wrong")


# This function is used to export the audit events to excel sheet.
async def export_audit_events_to_excel(search_result: dict, sqlserver_session: SqlServerDBSession):
    """Convert audit events search or recent results to Excel file"""
    try:
        # Extract events from search result
        events = search_result.get("events", [])
        event_count = len(events)
        logger.debug(f"Events to export: {events}")
        
        logger.info(f"Starting Excel export for {event_count} audit events")
        
        store_cache = {}  # cache to avoid repeated SQL Server lookups
        
        company_cache = {}  # cache to avoid repeated SQL Server lookups
        
        # Handle no events case by creating an empty DataFrame with headers
        if not events:
            logger.warning("No events found for Excel export - creating empty template")
            df = pd.DataFrame(columns=[
                "ID", "Event Timestamp", "Functionality", "Event Type", 
                "Store Name", "Company Name", "User", "Message", "Status", "Additional Data"
            ])
            
        # Process events and convert timestamps
        else:
            logger.debug(f"Processing {event_count} events for Excel conversion")
            data = []
            for event in events:
                # Handle both dicts and objects
                if isinstance(event, dict):
                    event_id = event.get("Id") or event.get("id")
                    ts = event.get("EventTimestamp") or event.get("event_timestamp")
                    functionality = event.get("Functionality") or event.get("functionality")
                    event_type = event.get("EventType") or event.get("event_type")
                    store_id = event.get("StoreLocationID") or event.get("store_id")
                    company_id = event.get("CompanyId") or event.get("company_id")
                    user = event.get("UserName") or event.get("user")
                    message = event.get("Message") or event.get("message")
                    status = event.get("Status") or event.get("status")
                    additional_data = event.get("AdditionalData") or event.get("additional_data")
                else:
                    # Pydantic model
                    event_id = event.Id
                    ts = event.EventTimestamp
                    functionality = event.Functionality
                    event_type = event.EventType
                    store_id = event.StoreLocationID
                    company_id = event.CompanyId
                    user = event.UserName
                    message = event.Message
                    status = event.Status
                    additional_data = event.AdditionalData
                
                # Handle and format EventTimestamp (handles both datetime and string)
                if ts:
                    if hasattr(ts, "strftime"):
                        timestamp_str = ts.strftime("%m-%d-%Y %H:%M:%S")
                    else:
                        try:
                            # Parse from "mmddyy hhmmss" format used in get_recent_events()
                            parsed_ts = datetime.strptime(ts, "%m%d%y %H%M%S")
                            timestamp_str = parsed_ts.strftime("%m-%d-%Y %H:%M:%S")
                        except Exception:
                            timestamp_str = ts  # fallback to raw string if parsing fails
                else:
                    timestamp_str = None
                    
                # Fetch StoreLocationName with caching
                if store_id in store_cache:
                    store_name = store_cache[store_id]
                else:
                    store_name = get_store_name(store_id, sqlserver_session)
                    store_cache[store_id] = store_name
                    
                # Fetch CompanyName with caching
                if company_id in company_cache:
                    company_name = company_cache[company_id]
                else:
                    company_name = get_company_name(company_id, sqlserver_session)
                    company_cache[company_id] = company_name
                
                # Append processed row
                data.append({
                    "ID": event_id,
                    "Event Timestamp": timestamp_str,
                    "Functionality": functionality,
                    "Event Type": event_type,
                    # "Store ID": store_id,
                    "Store Name": store_name,
                    # "Company ID": company_id,
                    "Company Name": company_name,
                    "User": user,
                    "Message": message,
                    "Status": status,
                    "Additional Data": json.dumps(additional_data) if additional_data else None
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            logger.debug("DataFrame created successfully with formatted timestamp strings")
        
        # Save Excel to memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Audit Events', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Audit Events']
            
            # Making header as bold
            header_font = Font(bold=True)
            for cell in next(worksheet.iter_rows(min_row=1, max_row=1)):
                cell.font = header_font
            
            # Auto-adjust the column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if cell.value and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except Exception:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        logger.info(f"Excel export done. File size={len(output.getvalue())} bytes")
        return output.getvalue()
        
    except Exception as e:
        logger.exception("Error creating Excel file:")
        raise HTTPException(status_code=500, detail="Something went wrong")
    

# This function is used to fetch the event type names based on functionality name
async def get_eventtypenames_by_functionalityname(functionalityname: str, session: AsyncSession) -> dict:
    """
    Fetch the event type names based on functionality name
    using the fun_get_eventtypes_by_functionality() PostgreSQL function.
    """
    try:
        logger.info(f"Fetching event type names for functionality: {functionalityname}")

        # Call the stored function to get event type names
        query = text("""
            SELECT * FROM fun_get_eventtypes_by_functionality(:functionalityname);
        """)
        
        # Execute the stored function
        result = await session.execute(query, {"functionalityname": functionalityname})

        # Convert to dict-like rows (so we can access by column name)
        rows = result.mappings().all()
        logger.debug(f"Fetched {len(rows)} event type(s): {rows}")

        # Handle no results
        if not rows:
            return {
                "StatusCode": 200,
                "message": "Data not found",
                "count": 0,
                "events": []
            }

        # Map rows to API response format
        events = [
            {
                "EventTypeID": row["eventtypeid"],
                "EventTypeName": row["eventtypename"]
            }
            for row in rows
        ]

        # Return response
        return {
            "StatusCode": 200,
            "message": "Data fetched successfully",
            "count": len(events),
            "events": events
        }

    except Exception as e:
        logger.exception(f"Error fetching eventtypenames by functionalityname:") # This will log full traceback
        raise HTTPException(status_code=500, detail=f"Something went wrong")


# This function is used to get all the auditfunctionalities.
async def get_all_auditfunctionalities(session: AsyncSession) -> dict:
    """
    Fetch all audit functionalities from the auditfunctionality table.
    """
    try:
        logger.info("Fetching all audit functionalities...")

        # Query to get all functionalities
        query = select(auditfunctionality_models.AuditFunctionality).order_by(auditfunctionality_models.AuditFunctionality.functionalityid)
        result = await session.execute(query)

        # Convert to dict-like rows (so we can access by column name)
        rows = result.scalars().all()
        logger.debug(f"Fetched {len(rows)} functionalities")

        # Handle no results
        if not rows:
            return {
                "StatusCode": 200,
                "message": "Data not found",
                "count": 0,
                "functionalities": []
            }

        # Map rows to API response format
        functionalities = [
            {
                "FunctionalityID": row.functionalityid,
                "FunctionalityName": row.functionalityname
            }
            for row in rows
        ]

        # Return response
        return {
            "StatusCode": 200,
            "message": "Data fetched successfully",
            "count": len(functionalities),
            "Data": functionalities
        }

    except Exception as e:
        logger.exception(f"Error fetching all audit functionalities:") # This will log full traceback
        raise HTTPException(status_code=500, detail=f"Something went wrong")
    

# This function is used to get all the companies.
async def get_all_companies(session) -> dict:
    """
    Fetch all companies from the company table.
    """
    try:
        logger.info("Fetching all companies...")

        # Query to get all companies
        query = select(company_models.Company).order_by(company_models.Company.CompanyName)
        result = session.execute(query)

        # Convert to dict-like rows (so we can access by column name)
        rows = result.scalars().all()
        logger.debug(f"Fetched {len(rows)} companies")

        # Handle no results
        if not rows:
            return {
                "StatusCode": 200,
                "message": "Data not found",
                "count": 0,
                "Data": []
            }

        # Map rows to API response format
        companies = [
            {
                "CompanyID": row.CompanyID,
                "CompanyName": row.CompanyName
            }
            for row in rows
        ]

        # Return response
        return {
            "StatusCode": 200,
            "message": "Data fetched successfully",
            "count": len(companies),
            "Data": companies
        }

    except Exception as e:
        logger.exception(f"Error fetching all companies:") # This will log full traceback
        raise HTTPException(status_code=500, detail=f"Something went wrong")
    

# This function is used to get all store locations for a given company.
async def get_store_locations_by_company(company_id: int, session) -> dict:
    """
    Fetch all store locations for a given company from the storelocation table.
    """
    try:
        logger.info(f"Fetching store locations for CompanyID={company_id}")

        # Query to get store locations by company ID
        query = select(store_location_models.StoreLocation).where(
            store_location_models.StoreLocation.CompanyID == company_id
        ).order_by(store_location_models.StoreLocation.StoreName)
        result = session.execute(query)

        # Convert to dict-like rows (so we can access by column name)
        rows = result.scalars().all()
        logger.debug(f"Fetched {len(rows)} store locations")

        # Handle no results
        if not rows:
            return {
                "StatusCode": 200,
                "message": "Data not found",
                "count": 0,
                "Data": []
            }

        # Map rows to API response format
        store_locations = [
            {   
                "CompanyID": row.CompanyID,
                "StoreLocationID": row.StoreLocationID,
                "StoreName": row.StoreName
            }
            for row in rows
        ]

        # Return response
        return {
            "StatusCode": 200,
            "message": "Data fetched successfully",
            "count": len(store_locations),
            "Data": store_locations
        }

    except Exception as e:
        logger.exception(f"Error fetching store locations by company ID:") # This will log full traceback
        raise HTTPException(status_code=500, detail=f"Something went wrong")