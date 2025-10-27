from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, JSON, func
from app.configurations.dbconfig import PG_BASE

# we are using PG_BASE here because this model is part of the audit service which uses PostgreSQL
class AuditEventArchival(PG_BASE):
    __tablename__ = "AuditEvents_Archival"

    id = Column(BigInteger, primary_key=True)
    eventtimestamp = Column(DateTime(timezone=True), nullable=False)
    functionalityid = Column(Integer, nullable=False)
    eventtypeid = Column(Integer, nullable=False)
    storelocationid = Column(BigInteger, nullable=True)
    companyid = Column(BigInteger, nullable=False)
    username = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    additionaldata = Column(JSON, nullable=True)
    archivedat = Column(DateTime(timezone=True), nullable=False, server_default=func.now())