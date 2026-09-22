"""
软电话 API - 呼入模块

处理前端 Workbench SDK 推送的通话事件，保存到数据库。
提供客户信息查询和通话记录查询接口。
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from models.database import get_db, Customer, CallRecord
from datetime import datetime
import uuid
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/softphone", tags=["Softphone"])

# 系统 DID（呼入号码）
SYSTEM_DID = os.getenv("CCC_CALLER_NUMBER") or os.getenv("CCC_DID")


def detect_call_direction(call_type: str, caller: str, callee: str) -> str:
    """
    检测通话方向：inbound（呼入）或 outbound（呼出）

    优先级：
    1. call_type 显式字段
    2. 通过号码推断（与系统 DID 比较）
    """
    if call_type:
        ct = str(call_type).lower()
        if ct in ("inbound", "in", "incoming"):
            return "inbound"
        if ct in ("outbound", "out", "outgoing"):
            return "outbound"

    if SYSTEM_DID:
        if caller == SYSTEM_DID:
            return "outbound"
        if callee == SYSTEM_DID:
            return "inbound"

    return "outbound"


def get_customer_phone(direction: str, caller: str, callee: str) -> str:
    """根据通话方向，返回客户号码"""
    return caller if direction == "inbound" else (callee or "")


def find_or_create_customer(db: Session, phone: str, direction: str) -> Customer | None:
    """查找或创建客户，phone 为空时返回 None"""
    if not phone:
        return None

    customer = db.query(Customer).filter(Customer.phone == phone).first()
    if customer:
        return customer

    suffix = phone[-4:] if len(phone) >= 4 else phone
    customer = Customer(
        id=str(uuid.uuid4()),
        name=f"客户{suffix}",
        phone=phone,
        notes=f"自动创建（来自软电话，{direction}通话）",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    logger.info(f"自动创建客户 - phone: {phone}, direction: {direction}, id: {customer.id}")
    return customer


def find_call_record(db: Session, call_id: str | None, contact_id: str | None) -> CallRecord | None:
    """根据 call_id 或 contact_id 查找通话记录"""
    if call_id:
        record = db.query(CallRecord).filter(CallRecord.call_id == call_id).first()
        if record:
            return record
    if contact_id:
        return db.query(CallRecord).filter(CallRecord.contact_id == contact_id).first()
    return None


# ========== 通话事件处理 ==========

@router.post("/call-event")
async def handle_call_event(request: Request, db: Session = Depends(get_db)):
    """
    接收前端软电话推送的通话事件

    事件类型:
    - call_coming: 来电振铃 → 创建通话记录
    - call_dialing: 外呼振铃 → 创建通话记录
    - call_establish: 通话接通 → 更新状态为 answered
    - call_release: 通话结束 → 更新状态为 completed，记录时长
    """
    try:
        payload = await request.json()
        event_type = payload.get("event_type") or payload.get("eventType")
        call_detail = payload.get("call_detail") or payload.get("callDetail") or payload

        logger.info(f"收到软电话事件: {event_type}, detail={call_detail}")

        if not event_type:
            raise HTTPException(status_code=400, detail="缺少 event_type")

        # 提取字段（兼容多种命名风格）
        call_id = call_detail.get("call_id") or call_detail.get("callId") or call_detail.get("jobId")
        contact_id = call_detail.get("contact_id") or call_detail.get("contactId") or call_detail.get("channelId")
        caller = call_detail.get("caller") or call_detail.get("callerNumber") or call_detail.get("caller_number") or ""
        callee = call_detail.get("callee") or call_detail.get("calleeNumber") or call_detail.get("callee_number") or ""
        call_type = call_detail.get("call_type") or call_detail.get("callType")
        status = call_detail.get("status") or call_detail.get("contactDisposition") or "unknown"
        duration = call_detail.get("duration") or call_detail.get("callDuration") or 0
        release_time = call_detail.get("release_time") or call_detail.get("releaseTime")

        direction = detect_call_direction(call_type, caller, callee)
        customer_phone = get_customer_phone(direction, caller, callee)

        if event_type in ("call_coming", "call_dialing"):
            return _handle_call_start(db, direction, customer_phone, caller, callee, call_id, contact_id, call_type)
        elif event_type == "call_establish":
            return _handle_call_answered(db, call_id, contact_id)
        elif event_type == "call_release":
            return _handle_call_end(db, call_id, contact_id, customer_phone, caller, callee, call_type, status, duration, release_time)
        else:
            logger.warning(f"未知的事件类型: {event_type}")
            return {"success": False, "message": f"未知事件类型: {event_type}"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理软电话事件失败: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"处理事件失败: {str(e)}")


def _handle_call_start(db, direction, customer_phone, caller, callee, call_id, contact_id, call_type):
    """处理来电/外呼振铃：创建通话记录"""
    customer = find_or_create_customer(db, customer_phone, direction)

    record = CallRecord(
        id=str(uuid.uuid4()),
        customer_id=customer.id if customer else None,
        direction=direction,
        caller_number=caller or None,
        callee_number=callee or (SYSTEM_DID if direction == "inbound" else "unknown"),
        call_id=call_id,
        contact_id=contact_id,
        status="ringing",
        duration=0,
        started_at=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(record)
    db.commit()

    return {
        "success": True,
        "message": "通话记录已创建",
        "record_id": record.id,
        "direction": direction,
        "customer_phone": customer_phone,
    }


def _handle_call_answered(db, call_id, contact_id):
    """处理通话接通：更新状态"""
    record = find_call_record(db, call_id, contact_id)
    if record:
        record.status = "answered"
        record.started_at = datetime.now()
        record.updated_at = datetime.now()
        db.commit()
        return {"success": True, "message": "通话已接通", "record_id": record.id}

    logger.warning(f"call_establish: 找不到记录 call_id={call_id} contact_id={contact_id}")
    return {"success": False, "message": "未找到对应通话记录"}


def _handle_call_end(db, call_id, contact_id, customer_phone, caller, callee, call_type, status, duration, release_time):
    """处理通话结束：更新状态和时长，或创建完整记录"""
    record = find_call_record(db, call_id, contact_id)

    if record:
        record.status = status or "completed"
        if duration:
            record.duration = int(duration)
        if release_time:
            try:
                record.ended_at = datetime.fromtimestamp(int(release_time) / 1000)
            except (ValueError, TypeError):
                record.ended_at = datetime.now()
        else:
            record.ended_at = datetime.now()
        record.updated_at = datetime.now()
        db.commit()
        return {"success": True, "message": "通话记录已更新", "record_id": record.id}

    # 记录不存在，创建完整记录
    direction = detect_call_direction(call_type, caller, callee)
    customer = find_or_create_customer(db, customer_phone, direction)

    record = CallRecord(
        id=str(uuid.uuid4()),
        customer_id=customer.id if customer else None,
        direction=direction,
        caller_number=caller or None,
        callee_number=callee or (SYSTEM_DID if direction == "inbound" else "unknown"),
        call_id=call_id,
        contact_id=contact_id,
        status=status or "completed",
        duration=int(duration) if duration else 0,
        ended_at=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(record)
    db.commit()
    return {"success": True, "message": "通话记录已创建", "record_id": record.id}


# ========== 客户信息 ==========

@router.get("/customer-info")
async def get_customer_info(phone: str, db: Session = Depends(get_db)):
    """
    根据来电号码查询客户信息

    返回: 客户基本信息、历史通话次数、最近通话时间
    """
    try:
        customer = db.query(Customer).filter(Customer.phone == phone).first()
        if not customer:
            return {"success": True, "customer": None}

        call_count = db.query(CallRecord).filter(
            CallRecord.customer_id == customer.id
        ).count()

        last_call = db.query(CallRecord).filter(
            CallRecord.customer_id == customer.id
        ).order_by(CallRecord.started_at.desc()).first()

        return {
            "success": True,
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "phone": customer.phone,
                "call_count": call_count,
                "last_call_time": last_call.started_at.isoformat() if last_call and last_call.started_at else None,
                "notes": customer.notes,
            },
        }
    except Exception as e:
        logger.error(f"查询客户信息失败: {e}", exc_info=True)
        return {"success": False, "message": f"查询失败: {str(e)}", "customer": None}


# ========== 通话记录 ==========

@router.get("/call-records/recent")
async def get_recent_call_records(limit: int = 20, db: Session = Depends(get_db)):
    """获取最近的通话记录（供软电话页面展示）"""
    records = (
        db.query(CallRecord)
        .order_by(CallRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "success": True,
        "records": [r.to_dict() for r in records],
    }
