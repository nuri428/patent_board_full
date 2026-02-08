from sqlalchemy import Column, String, Text, Date, DateTime
from sqlalchemy.sql import func
from shared.database import Base


class PatentMaster(Base):
    """한국 특허 마스터 테이블"""

    __tablename__ = "patent_master"

    application_number = Column(String(13), primary_key=True)
    title = Column(Text)
    abstract = Column(Text)
    publication_number = Column(String(13))
    applicate_date = Column(Date)
    publication_date = Column(Date)
    registration_number = Column(String(13))
    registration_date = Column(Date)
    patent_status = Column(String(20))
    raw_data = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class ForeignPatentMaster(Base):
    """해외 특허 마스터 테이블 (미국/해외)"""

    __tablename__ = "foreign_patent_master"

    document_number = Column(String(100), primary_key=True)
    country_code = Column(String(2))
    application_number = Column(String(50))
    registration_number = Column(String(50))
    publication_number = Column(String(50))
    open_number = Column(String(50))
    priority_number = Column(String(200))
    priority_date = Column(Date)
    international_application_number = Column(String(50))
    international_application_date = Column(Date)
    international_open_number = Column(String(50))
    international_open_date = Column(Date)
    family_number = Column(String(50))
    vdk_vgw_key = Column(String(100))
    application_date = Column(Date)
    publication_date = Column(Date)
    registration_date = Column(Date)
    invention_name = Column(Text)
    abstract = Column(Text)
    patent_status = Column(String(20))
    raw_data = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
