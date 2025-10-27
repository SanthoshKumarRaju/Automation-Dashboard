from sqlalchemy import BigInteger, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.configurations.dbconfig import SQL_BASE

# we are using SQL_BASE here because this model is part of the SQL Server
class Company(SQL_BASE):
    __tablename__ = 'Company'

    CompanyID: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    CompanyLoginCode: Mapped[str] = mapped_column(String(50))
    CompanyTaxID: Mapped[str] = mapped_column(String(40), nullable=False)
    CompanyName: Mapped[str] = mapped_column(String(40))
    CompanyAddressLine1: Mapped[str] = mapped_column(String(40))
    CompanyAddressLine2: Mapped[str] = mapped_column(String(40))
    City: Mapped[str] = mapped_column(String(40))
    CountyCode: Mapped[str] = mapped_column(String(40))
    StateCode: Mapped[str] = mapped_column(String(2), ForeignKey('State.StateCode'), nullable=False)
    E_Mail: Mapped[str] = mapped_column(String(40))
    PhoneNo: Mapped[str] = mapped_column(String(40))
    Fax: Mapped[str] = mapped_column(String(40))
    SyncUser: Mapped[str] = mapped_column(String(50), nullable=False)
    SyncPwd: Mapped[str] = mapped_column(String(50), nullable=False)
    EnableMobileLogging: Mapped[bool] = mapped_column(Boolean, nullable=False)
    IsInPOSSyncStatus: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    IsJobber: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ZIPCode: Mapped[str] = mapped_column(String(20))
    IsActive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Fix: Use consistent relationship name
    store_locations = relationship("StoreLocation", back_populates="company")