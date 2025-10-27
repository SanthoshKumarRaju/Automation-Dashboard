from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, JSON, CheckConstraint, Identity
from sqlalchemy.orm import relationship
from app.configurations.dbconfig import PG_BASE

# we are using PG_BASE here because this model is part of the audit service which uses PostgreSQL
class AuditEvent(PG_BASE):
    __tablename__ = "auditevents"
    __table_args__ = (
        CheckConstraint("status IN ('Success', 'Failed')", name="chk_auditevents_status"),
        {"postgresql_partition_by": "RANGE (eventtimestamp)"},  # lowercase
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    eventtimestamp = Column(DateTime(timezone=True), primary_key=True)
    functionalityid = Column(Integer, ForeignKey("auditfunctionalities.functionalityid"), nullable=False)
    eventtypeid = Column(Integer, ForeignKey("auditeventtypes.eventtypeid"), nullable=False)
    storelocationid = Column(BigInteger, nullable=True)
    companyid = Column(BigInteger, nullable=False)
    username = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    additionaldata = Column(JSON, nullable=True)

    # Relationships
    functionality = relationship("AuditFunctionality", back_populates="events")
    event_type = relationship("AuditEventType", back_populates="events")
