"""
数据库模型定义
使用SQLAlchemy ORM
"""
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

# 获取项目根目录（backend的上级目录）
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 加载环境变量（从项目根目录）
load_dotenv(PROJECT_ROOT / ".env")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dental_ai.db")

# 如果是SQLite相对路径，转换为绝对路径（相对于项目根目录）
if DATABASE_URL.startswith("sqlite:///./"):
    db_filename = DATABASE_URL.replace("sqlite:///./", "")
    DATABASE_URL = f"sqlite:///{PROJECT_ROOT / db_filename}"

# 创建数据库引擎
# SQLite需要check_same_thread=False以支持多线程
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


class Customer(Base):
    """客户模型"""
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True)  # UUID
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联关系
    call_records = relationship("CallRecord", back_populates="customer", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="customer", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="customer", cascade="all, delete-orphan")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class CallRecord(Base):
    """通话记录模型"""
    __tablename__ = "call_records"

    id = Column(String(36), primary_key=True)  # UUID
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True, index=True)
    direction = Column(String(20), nullable=True)  # 通话方向: inbound(呼入) / outbound(呼出)
    caller_number = Column(String(30), nullable=True)  # 主叫号码(呼入时为客户号码)
    callee_number = Column(String(30), nullable=False)  # 被叫号码(呼出时为客户号码;呼入时为系统DID)
    call_id = Column(String(100), nullable=True, index=True)  # CCC返回的call_id
    contact_id = Column(String(100), nullable=True, index=True)  # CCC返回的contact_id
    status = Column(String(50), nullable=False, default=" initiated")  # 通话状态
    duration = Column(Integer, nullable=True, default=0)  # 通话时长（秒）
    recording_url = Column(Text, nullable=True)  # 录音URL
    started_at = Column(DateTime, nullable=True)  # 通话开始时间
    ended_at = Column(DateTime, nullable=True)  # 通话结束时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联关系
    customer = relationship("Customer", back_populates="call_records")

    def to_dict(self):
        """转换为字典"""
        # 映射 direction 到前端期望的 call_type 格式
        call_type = None
        if self.direction == "inbound":
            call_type = "Inbound"
        elif self.direction == "outbound":
            call_type = "Outbound"

        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "direction": self.direction,
            "call_type": call_type,  # 前端兼容字段
            "caller_number": self.caller_number,
            "callee_number": self.callee_number,
            "call_id": self.call_id,
            "contact_id": self.contact_id,
            "status": self.status,
            "duration": self.duration,
            "recording_url": self.recording_url,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Appointment(Base):
    """预约信息模型"""
    __tablename__ = "appointments"

    id = Column(String(36), primary_key=True)  # UUID
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    appointment_time = Column(DateTime, nullable=False)  # 预约时间
    service_type = Column(String(100), nullable=False)  # 服务类型（如：洗牙、补牙等）
    doctor_name = Column(String(100), nullable=True)  # 医生姓名
    status = Column(String(50), nullable=False, default="pending")  # 状态：pending/confirmed/completed/cancelled
    notes = Column(Text, nullable=True)  # 备注
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联关系
    customer = relationship("Customer", back_populates="appointments")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "appointment_time": self.appointment_time.isoformat() if self.appointment_time else None,
            "service_type": self.service_type,
            "doctor_name": self.doctor_name,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ChatSession(Base):
    """文本对话会话模型"""
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True)  # UUID
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)  # 百炼会话ID
    status = Column(String(50), nullable=False, default="active")  # 状态：active/closed
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联关系
    customer = relationship("Customer", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "session_id": self.session_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ChatMessage(Base):
    """文本对话消息模型"""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True)  # UUID
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user/assistant
    content = Column(Text, nullable=False)  # 消息内容
    created_at = Column(DateTime, default=datetime.now)

    # 关联关系
    session = relationship("ChatSession", back_populates="messages")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# 数据库操作工具函数
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库（创建所有表）"""
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建成功")

    # 迁移：为旧数据库添加新字段（如果不存在）
    migrate_add_call_record_fields(engine)


def migrate_add_call_record_fields(eng):
    """
    为 call_records 表添加 caller_number 和 direction 字段
    安全：如果字段已存在则跳过
    """
    from sqlalchemy import inspect, text
    inspector = inspect(eng)
    if "call_records" not in inspector.get_table_names():
        return

    existing_columns = {c["name"] for c in inspector.get_columns("call_records")}
    with eng.begin() as conn:
        if "caller_number" not in existing_columns:
            conn.execute(text("ALTER TABLE call_records ADD COLUMN caller_number VARCHAR(30)"))
            print("✓ 迁移: 添加 call_records.caller_number 字段")
        if "direction" not in existing_columns:
            conn.execute(text("ALTER TABLE call_records ADD COLUMN direction VARCHAR(20)"))
            print("✓ 迁移: 添加 call_records.direction 字段")


if __name__ == "__main__":
    # 直接运行时初始化数据库
    init_db()
