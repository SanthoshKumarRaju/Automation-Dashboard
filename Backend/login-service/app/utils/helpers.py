import pandas as pd
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

class DataHelper:
    @staticmethod
    def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Sanitize DataFrame by handling NaN and None values"""
        df_clean = df.copy()
        
        for col in df_clean.columns:
            # Convert to string and replace NaN/None
            df_clean[col] = df_clean[col].astype(str).replace(['nan', 'None', 'NaT'], '')
            
            # Trim whitespace
            df_clean[col] = df_clean[col].str.strip()
        
        return df_clean
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str or date_str in ['', 'None', 'NaT']:
            return None
        
        try:
            return pd.to_datetime(date_str, errors='coerce')
        except Exception as e:
            logger.warning(f"Failed to parse date: {date_str}, error: {str(e)}")
            return None
    
    @staticmethod
    def should_highlight_old_date(date_str: str, months_threshold: int = 6) -> bool:
        """Check if a date is older than threshold (for highlighting)"""
        date_obj = DataHelper.parse_date(date_str)
        if not date_obj:
            return True  # Highlight missing dates
        
        threshold_date = datetime.now() - timedelta(days=30 * months_threshold)
        return date_obj < threshold_date

class ValidationHelper:
    @staticmethod
    def validate_filters(filters: Dict[str, Any]) -> bool:
        """Validate filter parameters"""
        try:
            for key, value in filters.items():
                if not isinstance(key, str):
                    return False
                if value and not isinstance(value, (str, list)):
                    return False
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_sort_params(sort_column: str, sort_order: str) -> bool:
        """Validate sort parameters"""
        valid_orders = ['asc', 'desc', 'ASC', 'DESC']
        return sort_order in valid_orders

class PaginationHelper:
    @staticmethod
    def paginate_dataframe(df: pd.DataFrame, page: int, page_size: int) -> pd.DataFrame:
        """Paginate DataFrame"""
        if df.empty:
            return df
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return df.iloc[start_idx:end_idx]
    
    @staticmethod
    def calculate_total_pages(total_count: int, page_size: int) -> int:
        """Calculate total pages for pagination"""
        if total_count == 0:
            return 0
        return (total_count + page_size - 1) // page_size

class ExportHelper:
    @staticmethod
    def generate_filename(prefix: str, data_type: str) -> str:
        """Generate export filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{data_type}_{timestamp}.xlsx"
    
    @staticmethod
    def validate_export_data(data: List[Dict]) -> bool:
        """Validate data for export"""
        if not data:
            return False
        
        if not isinstance(data, list):
            return False
        
        if not all(isinstance(item, dict) for item in data):
            return False
        
        return True