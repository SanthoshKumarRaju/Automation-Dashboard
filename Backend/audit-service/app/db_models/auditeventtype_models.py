from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.configurations.dbconfig import PG_BASE

# we are using PG_BASE here because this model is part of the audit service which uses PostgreSQL
class AuditEventType(PG_BASE):
    __tablename__ = "auditeventtypes"
    __table_args__ = (
        UniqueConstraint("functionalityid", "eventtypename", name="uq_functionality_event"),
    )

    eventtypeid = Column(Integer, primary_key=True, autoincrement=True)
    functionalityid = Column(Integer, ForeignKey("auditfunctionalities.functionalityid"), nullable=False)
    eventtypename = Column(String(250), nullable=False)

    # Relationships
    functionality = relationship("AuditFunctionality", back_populates="event_types")
    events = relationship("AuditEvent", back_populates="event_type")