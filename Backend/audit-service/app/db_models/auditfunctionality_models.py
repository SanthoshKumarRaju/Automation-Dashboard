from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.configurations.dbconfig import PG_BASE

# we are using PG_BASE here because this model is part of the audit service which uses PostgreSQL
class AuditFunctionality(PG_BASE):
    __tablename__ = "auditfunctionalities"

    functionalityid = Column(Integer, primary_key=True, autoincrement=True)
    functionalityname = Column(String(250), unique=True, nullable=False)

    # Relationships
    event_types = relationship("AuditEventType", back_populates="functionality", cascade="all, delete-orphan")
    events = relationship("AuditEvent", back_populates="functionality")