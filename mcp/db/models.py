from sqlalchemy import Column, String, Date, DateTime, Integer, Text, BigInteger, JSON
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class KRPatent(Base):
    __tablename__ = "patent_master"

    application_number = Column(String(13), primary_key=True)
    title = Column(LONGTEXT, nullable=False)
    abstract = Column(LONGTEXT, nullable=True)
    publication_number = Column(String(13), nullable=True)
    applicate_date = Column(Date, nullable=True)
    publication_date = Column(Date, nullable=True)
    registration_number = Column(String(13), nullable=True)
    registration_date = Column(Date, nullable=True)
    patent_status = Column(String(20), nullable=False)
    raw_data = Column(LONGTEXT, nullable=True)
    created_at = Column(DateTime(6), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(6), nullable=False, default=lambda: datetime.now(timezone.utc))


class ForeignPatent(Base):
    __tablename__ = "foreign_patent_master"

    document_number = Column(String(100), primary_key=True)
    country_code = Column(String(2), nullable=False)
    application_number = Column(String(50), nullable=True)
    registration_number = Column(String(50), nullable=True)
    publication_number = Column(String(50), nullable=True)
    application_date = Column(Date, nullable=True)
    publication_date = Column(Date, nullable=True)
    registration_date = Column(Date, nullable=True)
    invention_name = Column(LONGTEXT, nullable=True)
    abstract = Column(LONGTEXT, nullable=True)
    patent_status = Column(String(20), nullable=False)
    raw_data = Column(LONGTEXT, nullable=True)
    created_at = Column(DateTime(6), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(6), nullable=False, default=lambda: datetime.now(timezone.utc))


# Link Tables - for future use in search queries
class ForeignPatentIPC(Base):
    __tablename__ = "foreign_patent_ipc"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ipc_id = Column(BigInteger, nullable=False)  # Maps to an ipc table, or just ID
    patent_id = Column(
        String(100), nullable=False
    )  # Links to foreign_patent_master.document_number


class ForeignPatentCorporation(Base):
    __tablename__ = "foreign_patent_corporation"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    corporation_id = Column(BigInteger, nullable=False)
    patent_id = Column(String(100), nullable=False)
    role = Column(String(3), nullable=False)


class ForeignPatentInventor(Base):
    __tablename__ = "foreign_patent_inventor"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(300), nullable=False)
    patent_id = Column(String(100), nullable=False)


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    
    id = Column(String(50), primary_key=True)
    analysis_type = Column(String(100), nullable=False)
    parameters = Column(JSON, nullable=True)
    status = Column(String(20), default="running")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    results_count = Column(Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'analysis_type': self.analysis_type,
            'parameters': self.parameters,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at is not None else None,
            'results_count': self.results_count
        }
