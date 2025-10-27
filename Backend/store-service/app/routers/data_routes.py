from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import ValidationError
from datetime import datetime
from app.services.data_service import data_service
from app.dtos.data_request_dtos import FilterRequest
from app.dtos.data_response_dtos import PaginationResponse, FilterOptionsResponse, UserRolesResponse, FilterOptionsResponsedata
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix='/api/data')


# This endpoint fetches store location data with filtering and pagination
@router.get("/store-data", response_model=PaginationResponse)
async def get_store_data(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    sort_column: str = Query("LatestEndDateTime"),
    sort_order: str = Query("desc"),
    pos_system_cd: str = Query(None),
    mnsp_id: str = Query(None)
):
    """Get store location data with filtering and pagination"""
    try:
        filters = {}
        if pos_system_cd:
            filters['POSSystemCD'] = pos_system_cd
        if mnsp_id:
            filters['MNSPID'] = mnsp_id
        
        filter_request = FilterRequest(
            filters=filters,
            sort_column=sort_column,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        
        df = data_service.get_store_data(
            filter_request.filters, 
            filter_request.sort_column, 
            filter_request.sort_order
        )
        
        total_count = len(df)
        total_pages = (total_count + filter_request.page_size - 1) // filter_request.page_size
        start_idx = (filter_request.page - 1) * filter_request.page_size
        end_idx = start_idx + filter_request.page_size
        paginated_data = df.iloc[start_idx:end_idx]
        
        response = PaginationResponse(
            statusCode=200,
            message="Data fetched successfully",
            total_count=total_count,
            page=filter_request.page,
            page_size=filter_request.page_size,
            total_pages=total_pages,
            data=paginated_data.to_dict(orient='records')
        )
        
        logger.info(f"Returning {len(paginated_data)} store records (page {filter_request.page})")
        return response
        
    except ValidationError as e:
        logger.warning(f"Store data validation error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid filter parameters")
    except Exception as e:
        logger.exception(f"Error fetching store data:") # This will log full traceback
        raise HTTPException(status_code=500, detail="Something went wrong")


# This endpoint fetches user data with filtering and pagination
@router.get("/user-data", response_model=PaginationResponse)
async def get_user_data(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    sort_column: str = Query("LastLogon"),
    sort_order: str = Query("desc"),
    user_role: str = Query(None),
    company_name: str = Query(None)
):
    """Get user data with filtering and pagination"""
    try:
        filters = {}
        if user_role:
            filters['UserRole'] = user_role
        if company_name:
            filters['CompanyName'] = company_name
        
        filter_request = FilterRequest(
            filters=filters,
            sort_column=sort_column,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        
        df = data_service.get_user_data(
            filter_request.filters, 
            filter_request.sort_column, 
            filter_request.sort_order
        )
        
        total_count = len(df)
        total_pages = (total_count + filter_request.page_size - 1) // filter_request.page_size
        start_idx = (filter_request.page - 1) * filter_request.page_size
        end_idx = start_idx + filter_request.page_size
        paginated_data = df.iloc[start_idx:end_idx]
        
        response = PaginationResponse(
            statusCode=200,
            message="Data fetched successfully",
            total_count=total_count,
            page=filter_request.page,
            page_size=filter_request.page_size,
            total_pages=total_pages,
            data=paginated_data.to_dict(orient='records')
        )
        
        logger.info(f"Returning {len(paginated_data)} user records (page {filter_request.page})")
        return response
        
    except ValidationError as e:
        logger.warning(f"User data validation error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid filter parameters")
    except Exception as e:
        logger.exception(f"Error fetching user data:")  # This will log full traceback
        raise HTTPException(status_code=500, detail="Failed to fetch user data")


# This endpoint provides unique filter values for store data
@router.get("/filters/unique", response_model=FilterOptionsResponse)
async def get_unique_filters():
    """Get unique filter values for store data"""
    try:
        filters = data_service.get_unique_filters()
        return FilterOptionsResponse(
            statusCode=200,
            message="Unique filters retrieved successfully",
            data=FilterOptionsResponsedata(**filters)
        )
    except Exception as e:
        logger.exception(f"Error fetching unique filters:") # This will log full traceback
        raise HTTPException(status_code=500, detail="Something went wrong")


# This endpoint provides unique user roles
@router.get("/filters/user-roles", response_model=UserRolesResponse)
async def get_user_roles():
    """Get unique user roles"""
    try:
        roles = data_service.get_user_roles()
        return UserRolesResponse(
            statusCode=200,
            message="User roles retrieved successfully",
            user_roles=roles
        )
    except Exception as e:
        logger.exception(f"Error fetching user roles:") # This will log full traceback
        raise HTTPException(status_code=500, detail="Something went wrong")


# This endpoint allows refreshing of data caches
@router.post(f"/refresh-all")
async def refresh_all_data():
    """Refresh all data caches"""
    try:
        success = data_service.refresh_data('all')
        if success:
            logger.info("All data caches refreshed via API")
            return {
                "statusCode": 200,
                "message": "All data refreshed successfully"
            }
        else:
            return {
                "statusCode": 400,
                "message": "Partial refresh completed with warnings"
            }
    except Exception as e:
        logger.exception(f"Failed to refresh all data:")    # This will log full traceback
        raise HTTPException(status_code=500, detail="Something went wrong")