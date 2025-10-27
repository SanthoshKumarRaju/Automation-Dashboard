from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from datetime import datetime
from app.services.export_service import export_service
from app.dtos.export_request_dtos import ExportRequest
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix='/api/export')


# This endpoint exports store data to an Excel file
@router.post("/store-data")
async def export_store_data(
    export_request: ExportRequest
):
    """Export store data to Excel"""
    try:
        excel_file = export_service.export_store_data(export_request.data)
        
        logger.info(f"Exported {len(export_request.data)} store records to Excel")
        return StreamingResponse(
            excel_file,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename="store_data_export.xlsx"'}
        )
        
    except ValidationError as e:
        logger.warning(f"Export validation error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid export data")
    except Exception as e:
        logger.exception(f"Error exporting store data:")    # This will log full traceback
        raise HTTPException(status_code=500, detail="Something went wrong")


# This endpoint exports user data to an Excel file
@router.post("/user-data")
async def export_user_data(
    export_request: ExportRequest
):
    """Export user data to Excel"""
    try:
        excel_file = export_service.export_user_data(export_request.data)
        
        logger.info(f"Exported {len(export_request.data)} user records to Excel")
        return StreamingResponse(
            excel_file,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename="user_data_export.xlsx"'}
        )
        
    except ValidationError as e:
        logger.warning(f"Export validation error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid export data")
    except Exception as e:
        logger.exception(f"Error exporting user data:")     # This will log full traceback
        raise HTTPException(status_code=500, detail="Something went wrong")