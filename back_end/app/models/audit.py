from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from shared.database import Base


class AuditLog(Base):
    """시스템 감사 로그 테이블"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)  # 비로그인 요청일 수 있음
    username = Column(String(255), index=True, nullable=True)
    action = Column(
        String(100), index=True, nullable=False
    )  # login, search, report_gen, etc.
    resource_type = Column(String(50), index=True)  # patent, report, user
    resource_id = Column(String(255))
    description = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    status = Column(String(20))  # success, failure
    payload = Column(JSON, nullable=True)  # 추가 데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
