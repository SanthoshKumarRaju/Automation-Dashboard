import io
import pandas as pd
import openpyxl
from app.utils.logger import get_logger

logger = get_logger(__name__)

# This class handles exporting data to Excel files
class ExportService:
    def __init__(self):
        logger.info("Export service initialized with openpyxl")
    
    # This function exports store data to an Excel file
    def export_store_data(self, data):
        """Export store data to Excel format using openpyxl"""
        try:
            if not data:
                raise ValueError("No data provided for export")
            
            df = pd.DataFrame(data)
            df = self.clean_store_data(df)
            
            output = io.BytesIO()
            
            # Use openpyxl as engine
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Store Data')
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Store Data']
                
                # Adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Add basic header styling
                for cell in worksheet[1]:
                    cell.font = openpyxl.styles.Font(bold=True)
                    cell.fill = openpyxl.styles.PatternFill(start_color="DDEEFF", end_color="DDEEFF", fill_type="solid")
            
            output.seek(0)
            logger.info(f"Exported {len(df)} store records to Excel using openpyxl")
            return output
            
        except Exception as e:
            logger.error(f"Failed to export store data: {str(e)}")
            raise
    
    # This function exports user data to an Excel file
    def export_user_data(self, data):
        """Export user data to Excel format using openpyxl"""
        try:
            if not data:
                raise ValueError("No data provided for export")
            
            df = pd.DataFrame(data)
            df = self.clean_user_data(df)
            
            output = io.BytesIO()
            
            # Use openpyxl as engine
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='User Data')
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['User Data']
                
                # Adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Add basic header styling
                for cell in worksheet[1]:
                    cell.font = openpyxl.styles.Font(bold=True)
                    cell.fill = openpyxl.styles.PatternFill(start_color="DDEEFF", end_color="DDEEFF", fill_type="solid")
            
            output.seek(0)
            logger.info(f"Exported {len(df)} user records to Excel using openpyxl")
            return output
            
        except Exception as e:
            logger.error(f"Failed to export user data: {str(e)}")
            raise
    
    # This function cleans and renames store data columns
    def clean_store_data(self, df):
        """Clean and rename store data columns"""
        df = df.rename(columns={'PaymentSystemsProductName': 'fuelbrand'})
        
        # Reorder columns
        desired_order = [
            "StoreLocationID", "POSSystemCD", "CompanyID", "StoreName", 
            "ZIPCode", "IsPCLess", "MNSPID", "fuelbrand", "SiteIP", 
            "Scandata", "RCN", "LatestEndDateTime"
        ]
        
        # Only include columns that exist in the DataFrame
        existing_columns = [col for col in desired_order if col in df.columns]
        return df[existing_columns]
    
    # This function cleans and renames user data columns
    def clean_user_data(self, df):
        """Clean and rename user data columns"""
        # Reorder columns
        desired_order = [
            "CompanyID", "CompanyName", "StoreID", "StoreName", 
            "UserName", "UserRole", "UserMail", "LastLogon"
        ]
        
        # Only include columns that exist in the DataFrame
        existing_columns = [col for col in desired_order if col in df.columns]
        return df[existing_columns]

# Global export service instance
export_service = ExportService()