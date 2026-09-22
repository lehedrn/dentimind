"""
Webhook API路由
处理CCC通话结果回调（仅呼出）

呼入通话由 softphone.py 处理（前端 SDK 推送事件）
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from models.database import get_db, Customer, CallRecord
from datetime import datetime
import uuid
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhook", tags=["Webhook"])

# 系统 DID（呼入号码）
SYSTEM_DID = os.getenv("CCC_CALLER_NUMBER") or os.getenv("CCC_DID")


def detect_call_direction(callback_data: dict, caller_number: str, callee_number: str) -> str:
    """
    检测通话方向：inbound（呼入）或 outbound（呼出）

    优先级：
    1. CCC显式提供的方向字段
    2. 通过号码判断
    """
    # 1. 显式字段
    for key in ("direction", "call_direction", "call_type", "CallType", "Direction"):
        val = callback_data.get(key)
        if val:
            val_lower = str(val).lower()
            if val_lower in ("inbound", "in", "incoming"):
                return "inbound"
            if val_lower in ("outbound", "out", "outgoing"):
                return "outbound"

    # 2. 号码推断
    if SYSTEM_DID:
        if caller_number == SYSTEM_DID:
            return "outbound"
        if callee_number == SYSTEM_DID:
            return "inbound"

    return "outbound"


def get_customer_phone(direction: str, caller_number: str, callee_number: str) -> str:
    """根据通话方向，返回客户号码"""
    if direction == "inbound":
        return caller_number or ""
    else:
        return callee_number or ""


def find_or_create_customer(db: Session, phone: str, direction: str) -> Customer:
    """查找或创建客户"""
    if not phone:
        return None

    customer = db.query(Customer).filter(Customer.phone == phone).first()
    if not customer:
        suffix = phone[-4:] if len(phone) >= 4 else phone
        customer = Customer(
            id=str(uuid.uuid4()),
            name=f"客户{suffix}",
            phone=phone,
            notes=f"自动创建（来自Webhook，{direction}通话）",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        logger.info(f"Webhook自动创建客户 - phone: {phone}, direction: {direction}, id: {customer.id}")

    return customer


@router.post("/ccc/call-ended")
async def ccc_call_ended_webhook(request: Request, db: Session = Depends(get_db)):
    """
    CCC通话结束回调（仅处理呼出通话）

    呼入通话由前端 SDK 推送到 /api/softphone/call-event
    这里只处理呼出通话的回调（外呼时系统会创建通话记录，通话结束后 CCC 推送回调）
    """
    try:
        callback_data = await request.json()
        logger.info(f"收到CCC通话结束回调: {callback_data}")

        # 提取关键字段（兼容多种命名风格）
        call_id = callback_data.get("call_id") or callback_data.get("CallId")
        contact_id = callback_data.get("contact_id") or callback_data.get("ContactId")
        callee_number = callback_data.get("callee") or callback_data.get("Callee") or ""
        caller_number = callback_data.get("caller") or callback_data.get("Caller") or ""
        status = callback_data.get("status") or callback_data.get("Status")
        duration = callback_data.get("duration") or callback_data.get("Duration", 0)
        start_time = callback_data.get("start_time") or callback_data.get("StartTime")
        end_time = callback_data.get("end_time") or callback_data.get("EndTime")
        recording_url = callback_data.get("recording_url") or callback_data.get("RecordingUrl")

        if not call_id and not contact_id:
            logger.warning(f"回调数据缺少call_id或contact_id: {callback_data}")
            raise HTTPException(status_code=400, detail="缺少通话标识")

        # 检测通话方向
        direction = detect_call_direction(callback_data, caller_number, callee_number)
        customer_phone = get_customer_phone(direction, caller_number, callee_number)

        logger.info(
            f"通话方向: {direction}, caller={caller_number}, "
            f"callee={callee_number}, customer_phone={customer_phone}"
        )

        # 如果是呼入通话，忽略（由 softphone.py 处理）
        if direction == "inbound":
            logger.info(f"呼入通话回调，由 softphone.py 处理，忽略")
            return {
                "success": True,
                "message": "呼入通话已由 softphone 处理",
                "call_id": call_id,
                "direction": direction
            }

        # 查找通话记录（外呼时会预先创建）
        call_record = None
        if call_id:
            call_record = db.query(CallRecord).filter(CallRecord.call_id == call_id).first()
        if not call_record and contact_id:
            call_record = db.query(CallRecord).filter(CallRecord.contact_id == contact_id).first()

        if not call_record:
            # 通话记录不存在，创建
            customer = find_or_create_customer(db, customer_phone, direction)

            call_record = CallRecord(
                id=str(uuid.uuid4()),
                customer_id=customer.id if customer else None,
                direction=direction,
                caller_number=caller_number or None,
                callee_number=callee_number or (SYSTEM_DID if direction == "inbound" else "unknown"),
                call_id=call_id,
                contact_id=contact_id,
                status=status or "unknown",
                duration=int(duration) if duration else 0,
                recording_url=recording_url,
                started_at=datetime.fromtimestamp(int(start_time) / 1000) if start_time else None,
                ended_at=datetime.fromtimestamp(int(end_time) / 1000) if end_time else None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(call_record)
            logger.info(
                f"Webhook创建通话记录 - call_id: {call_id}, contact_id: {contact_id}, "
                f"direction: {direction}, customer: {customer_phone}"
            )
        else:
            # 更新已存在的通话记录
            if status:
                call_record.status = status
            if duration:
                call_record.duration = int(duration)
            if recording_url:
                call_record.recording_url = recording_url
            if start_time:
                call_record.started_at = datetime.fromtimestamp(int(start_time) / 1000)
            if end_time:
                call_record.ended_at = datetime.fromtimestamp(int(end_time) / 1000)
            if not call_record.direction:
                call_record.direction = direction
            if not call_record.caller_number:
                call_record.caller_number = caller_number or None
            call_record.updated_at = datetime.now()
            logger.info(
                f"Webhook更新通话记录 - call_id: {call_id}, status: {status}, "
                f"direction: {direction}"
            )

        db.commit()

        return {
            "success": True,
            "message": "通话记录已保存",
            "call_id": call_id,
            "contact_id": contact_id,
            "direction": direction,
            "customer_phone": customer_phone
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理CCC通话结束回调失败: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"处理回调失败: {str(e)}")


@router.post("/ccc/test")
async def test_webhook(request: Request):
    """测试Webhook接口"""
    try:
        data = await request.json()
        logger.info(f"收到测试Webhook请求: {data}")
        return {
            "success": True,
            "message": "Webhook测试成功",
            "received_data": data
        }
    except Exception as e:
        logger.error(f"测试Webhook失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "webhook"
    }
