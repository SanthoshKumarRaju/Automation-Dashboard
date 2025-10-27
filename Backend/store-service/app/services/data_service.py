import pandas as pd
from app.configurations.database import db_manager
from app.utils.logger import get_logger
from app.sql.queries import STORE_DATA_QUERY, USER_DATA_QUERY

logger = get_logger(__name__)


class DataService:
    """Service for managing data loading, caching, filtering, and sorting."""

    def __init__(self):
        self.store_data_df = pd.DataFrame()
        self.user_data_df = pd.DataFrame()
        self._store_data_loaded = False
        self._user_data_loaded = False
        logger.info("Data service initialized")


    # This function is used to Load Store Data
    def load_store_data(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load store location data from the database."""
        try:
            if self._store_data_loaded and not force_refresh and not self.store_data_df.empty:
                logger.debug("Using cached store data")
                return self.store_data_df

            logger.info("Executing store data query...")
            self.store_data_df = pd.read_sql(STORE_DATA_QUERY, db_manager.engine)

            if self.store_data_df.empty:
                logger.warning("Store data query returned empty results")
            else:
                # Add serial numbers
                self.store_data_df.insert(0, 'SerialNumber', range(1, len(self.store_data_df) + 1))

                # Convert datetime safely if exists
                if "LatestEndDateTime" in self.store_data_df.columns:
                    self.store_data_df["LatestEndDateTime"] = pd.to_datetime(
                        self.store_data_df["LatestEndDateTime"], errors="coerce"
                    )

            self._store_data_loaded = True
            logger.info(f"Loaded {len(self.store_data_df)} store records from database")
            return self.store_data_df

        except Exception as e:
            logger.exception(f"Failed to load store data:")    # This will log full traceback
            self._store_data_loaded = False
            return pd.DataFrame()


    # This function is used to Load User Data
    def load_user_data(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load user data from the database."""
        try:
            if self._user_data_loaded and not force_refresh and not self.user_data_df.empty:
                logger.debug("Using cached user data")
                return self.user_data_df

            logger.info("Executing user data query...")
            self.user_data_df = pd.read_sql(USER_DATA_QUERY, db_manager.engine)

            if self.user_data_df.empty:
                logger.warning("User data query returned empty results")
            else:
                # Add serial numbers
                self.user_data_df.insert(0, 'SerialNumber', range(1, len(self.user_data_df) + 1))

            self._user_data_loaded = True
            logger.info(f"Loaded {len(self.user_data_df)} user records from database")
            return self.user_data_df

        except Exception as e:
            logger.exception(f"Failed to load user data:")  # This will log full traceback
            self._user_data_loaded = False
            return pd.DataFrame()

    # This function get Store Data (with filtering/sorting)
    def get_store_data(self, filters=None, sort_column="LatestEndDateTime", sort_order="desc") -> pd.DataFrame:
        """Get store data with optional filtering and sorting."""
        try:
            df = self.load_store_data()

            if df.empty:
                return df

            if filters:
                df = self.apply_filters(df, filters)

            df = self.apply_sorting(df, sort_column, sort_order)

            if "LatestEndDateTime" in df.columns:
                df["LatestEndDateTime"] = df["LatestEndDateTime"].apply(
                    lambda x: str(x) if pd.notnull(x) else "No Data"
                )

            return df

        except Exception as e:
            logger.exception(f"Error processing store data:")   # This will log full traceback
            return pd.DataFrame()


    # This function get User Data (with filtering/sorting)
    def get_user_data(self, filters=None, sort_column="LastLogon", sort_order="desc") -> pd.DataFrame:
        """Get user data with optional filtering and sorting."""
        try:
            df = self.load_user_data()

            if df.empty:
                return df

            if filters:
                df = self.apply_filters(df, filters)

            df = self.apply_sorting(df, sort_column, sort_order)

            if "LastLogon" in df.columns:
                df["LastLogon"] = df["LastLogon"].apply(
                    lambda x: str(x) if pd.notnull(x) else "No Data"
                )

            return df

        except Exception as e:
            logger.exception(f"Error processing user data:")    # This will log full traceback
            return pd.DataFrame()

    # This functions apply's filters 
    def apply_filters(self, df: pd.DataFrame, filters: dict) -> pd.DataFrame:
        """Apply filters to DataFrame."""
        try:
            filtered_df = df.copy()

            for col, value in filters.items():
                if value and col in filtered_df.columns:
                    if isinstance(value, list):
                        mask = filtered_df[col].astype(str).str.lower().isin(
                            [str(v).lower() for v in value]
                        )
                        filtered_df = filtered_df[mask]
                    else:
                        filtered_df = filtered_df[
                            filtered_df[col].astype(str).str.contains(str(value), case=False, na=False)
                        ]

            return filtered_df

        except Exception as e:
            logger.exception(f"Error applying filters:") # This will log full traceback
            return df

    # This function applies sorting to a DataFrame based on a specified column and order
    def apply_sorting(self, df: pd.DataFrame, sort_column: str, sort_order: str) -> pd.DataFrame:
        """Apply sorting to DataFrame."""
        try:
            if df.empty or sort_column not in df.columns:
                return df

            ascending = sort_order.lower() == "asc"

            if sort_column in ["LatestEndDateTime", "LastLogon"]:
                df = df.sort_values(
                    by=sort_column,
                    ascending=ascending,
                    key=lambda x: pd.to_datetime(x, errors="coerce"),
                )
            else:
                df = df.sort_values(by=sort_column, ascending=ascending)

            return df

        except Exception as e:
            logger.exception(f"Error applying sorting:") # This will log full traceback
            return df

    # This function retrieves unique filter values from the store data
    def get_unique_filters(self) -> dict:
        """Get unique values for filter dropdowns."""
        try:
            df = self.load_store_data()

            if df.empty:
                return {
                    'StatusCode': 200,
                    'message': "No data found",
                    'POSSystemCD': [], 
                    'MNSPID': [], 
                    'PaymentSystemsProductName': []
                }

            return {
                'StatusCode': 200,
                'message': "Data fetched successfully",
                'POSSystemCD': sorted(df['POSSystemCD'].dropna().unique().tolist()) if 'POSSystemCD' in df.columns else [],
                'MNSPID': sorted(df['MNSPID'].dropna().unique().tolist()) if 'MNSPID' in df.columns else [],
                'PaymentSystemsProductName': sorted(df['PaymentSystemsProductName'].dropna().unique().tolist())
                if 'PaymentSystemsProductName' in df.columns else [],
            }

        except Exception as e:
            logger.exception(f"Error getting unique filters:") # This will log full traceback
            return {'POSSystemCD': [], 'MNSPID': [], 'PaymentSystemsProductName': []}

    # This function retrieves unique user roles from the user data  
    def get_user_roles(self) -> list:
        """Get unique user roles."""
        try:
            df = self.load_user_data()

            if df.empty or "UserRole" not in df.columns:
                return [] 

            roles = sorted(df["UserRole"].dropna().unique().tolist())
            return roles  

        except Exception as e:
            logger.exception(f"Error getting user roles:")  # This will log full traceback
            return []  
    
    # This function is used to freshed the data
    def refresh_data(self, data_type='all'):
        """Refresh data cache"""
        try:
            if data_type in ['store', 'all']:
                self._store_data_loaded = False
                self.load_store_data(force_refresh=True)
                logger.info("Store data cache refreshed")
            
            if data_type in ['user', 'all']:
                self._user_data_loaded = False
                self.load_user_data(force_refresh=True)
                logger.info("User data cache refreshed")
            
            return True
        except Exception as e:
            logger.exception(f"Error refreshing data:")  # This will log full traceback
            return False

# Global data service instance
data_service = DataService()
