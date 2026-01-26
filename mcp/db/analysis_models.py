from sqlalchemy import Column, String, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date
import uuid


Base = declarative_base()


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    analysis_type = Column(String(50))
    status = Column(String(20), default="running")
    parameters = Column(JSON)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String(500), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "analysis_type": self.analysis_type,
            "status": self.status,
            "parameters": self.parameters,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message
        }