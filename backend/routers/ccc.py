"""
CCC电话API路由
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from services.aliyun_ccc import CCCService
from models.database import get_db, Customer, CallRecord
from datetime import datetime
import uuid
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ccc", tags=["CCC"])

ccc_service = CCCService()
SYSTEM_DID = os.getenv("CCC_CALLER_NUMBER") or os.getenv("CCC_DID")


@router.post("/outbound-call")
async def make_outbound_call(callee_number: str, db: Session = Depends(get_db)):
    """
    发起外呼

    Args:
        callee_number: 被叫号码（手机号）

    Returns:
        通话ID和状态
    """
    try:
        logger.info(f"收到外呼请求 - callee_number: {callee_number}")

        # 简单的手机号验证
        if not callee_number or len(callee_number) != 11 or not callee_number.isdigit():
            raise HTTPException(status_code=400, detail="无效的手机号格式")

        # 外呼前，先查找或创建客户
        customer = db.query(Customer).filter(Customer.phone == callee_number).first()
        if not customer:
            # 客户不存在，自动创建
            customer = Customer(
                id=str(uuid.uuid4()),
                name=f"客户{callee_number[-4:]}",  # 使用手机后4位作为默认名称
                phone=callee_number,
                notes="自动创建（来自外呼）",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)
            logger.info(f"自动创建客户 - phone: {callee_number}, id: {customer.id}")

        # 创建初步的通话记录（外呼前）
        call_record = CallRecord(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            direction="outbound",
            caller_number=SYSTEM_DID,
            callee_number=callee_number,
            status="initiating",  # 发起中
            duration=0,
            started_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(call_record)
        db.commit()
        db.refresh(call_record)
        logger.info(f"创建通话记录 - record_id: {call_record.id}, customer_id: {customer.id}")

        # 发起外呼
        result = await ccc_service.make_call(callee_number)

        # 外呼成功后，更新通话记录
        try:
            raw_call_id = result.get("call_id") or ""
            raw_contact_id = result.get("contact_id")
            # 防御：如果 call_id 看起来像整个响应体（长度过长或包含 JSON 特征），只保留合理部分
            if len(raw_call_id) > 100 or raw_call_id.startswith("{"):
                logger.warning(
                    f"call_id 异常（可能包含整个响应体），已丢弃: {raw_call_id[:80]}..."
                )
                raw_call_id = None
            call_record.call_id = raw_call_id or call_record.call_id
            call_record.contact_id = raw_contact_id
            call_record.status = result.get("status", "initiated")
            call_record.updated_at = datetime.now()
            db.commit()
            logger.info(
                f"更新通话记录 - call_id: {call_record.call_id}, "
                f"contact_id: {call_record.contact_id}, status: {call_record.status}"
            )
        except Exception as db_error:
            logger.error(f"更新通话记录失败: {str(db_error)}")
            db.rollback()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"外呼失败: {str(e)}")
        # 外呼失败时，更新通话记录状态
        try:
            if 'call_record' in locals():
                call_record.status = "failed"
                call_record.updated_at = datetime.now()
                db.commit()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"外呼失败: {str(e)}")


@router.get("/call-records")
async def list_call_records(start_time: int, end_time: int, page_number: int = 1, page_size: int = 50):
    """
    查询通话记录

    Args:
        start_time: 开始时间（Unix时间戳，毫秒）
        end_time: 结束时间（Unix时间戳，毫秒）
        page_number: 页码
        page_size: 每页数量

    Returns:
        通话记录列表
    """
    try:
        logger.info(f"查询通话记录 - start_time: {start_time}, end_time: {end_time}")

        records = await ccc_service.list_call_records(start_time, end_time, page_number, page_size)

        # 转换为字典格式，确保字段名一致
        records_dict = []
        for record in records:
            if hasattr(record, 'to_map'):
                record_dict = record.to_map()
                # 将驼峰命名转换为下划线命名
                record_dict = {
                    'called_number': record_dict.get('CalledNumber', ''),
                    'calling_number': record_dict.get('CallingNumber', ''),
                    'contact_type': record_dict.get('ContactType', ''),
                    'contact_disposition': record_dict.get('ContactDisposition', ''),
                    'call_duration': record_dict.get('CallDuration', 0),
                    'start_time': record_dict.get('StartTime', 0),
                    'recording_ready': record_dict.get('RecordingReady', False),
                    'contact_id': record_dict.get('ContactId', ''),
                    'release_time': record_dict.get('ReleaseTime', 0),
                    'established_time': record_dict.get('EstablishedTime', 0),
                }
            else:
                record_dict = {
                    'called_number': getattr(record, 'CalledNumber', ''),
                    'calling_number': getattr(record, 'CallingNumber', ''),
                    'contact_type': getattr(record, 'ContactType', ''),
                    'contact_disposition': getattr(record, 'ContactDisposition', ''),
                    'call_duration': getattr(record, 'CallDuration', 0),
                    'start_time': getattr(record, 'StartTime', 0),
                    'recording_ready': getattr(record, 'RecordingReady', False),
                    'contact_id': getattr(record, 'ContactId', ''),
                    'release_time': getattr(record, 'ReleaseTime', 0),
                    'established_time': getattr(record, 'EstablishedTime', 0),
                }
            records_dict.append(record_dict)

        return {"records": records_dict}

    except Exception as e:
        logger.error(f"查询通话记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询通话记录失败: {str(e)}")


@router.get("/call-detail/{contact_id}")
async def get_call_detail(contact_id: str):
    """
    获取通话详情

    Args:
        contact_id: 通话ID

    Returns:
        通话详情
    """
    try:
        logger.info(f"获取通话详情 - contact_id: {contact_id}")

        detail = await ccc_service.get_call_detail(contact_id)
        return detail

    except Exception as e:
        logger.error(f"获取通话详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取通话详情失败: {str(e)}")


@router.get("/recording/{contact_id}")
async def get_recording_url(contact_id: str):
    """
    获取录音（直接返回音频流）

    Args:
        contact_id: 通话ID

    Returns:
        录音文件流
    """
    try:
        logger.info(f"获取录音 - contact_id: {contact_id}")

        url = await ccc_service.get_recording_url(contact_id)

        if not url:
            raise HTTPException(status_code=404, detail="录音不存在")

        # 直接重定向到录音URL
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=url, status_code=302)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取录音失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取录音失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    健康检查
    """
    return {
        "status": "ok",
        "service": "ccc",
        "configured": ccc_service.client is not None
    }


@router.get("/agent/status")
async def get_agent_status():
    """
    获取坐席状态

    Returns:
        {
            "agent_status": "坐席状态",
            "is_online": True/False,
            "user_id": "坐席ID"
        }
    """
    try:
        logger.info("查询坐席状态")

        status = await ccc_service.check_agent_status()

        return {
            "success": True,
            **status
        }

    except Exception as e:
        logger.error(f"查询坐席状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询坐席状态失败: {str(e)}")


@router.post("/agent/sign-in")
async def sign_in_agent():
    """
    手动签到坐席（使坐席上线）

    Returns:
        {
            "success": True/False,
            "message": "签到结果信息"
        }
    """
    try:
        logger.info("手动签到坐席")

        result = await ccc_service.sign_in_agent()

        return result

    except Exception as e:
        logger.error(f"签到坐席失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"签到坐席失败: {str(e)}")


@router.post("/agent/ensure-online")
async def ensure_agent_online(auto_sign_in: bool = True):
    """
    确保坐席在线（检查状态，如果不在线则自动签到）

    Args:
        auto_sign_in: 如果不在线，是否自动签到

    Returns:
        {
            "is_online": True/False,
            "agent_status": "坐席状态",
            "action_taken": "采取的操作",
            "success": True/False
        }
    """
    try:
        logger.info(f"确保坐席在线 - auto_sign_in: {auto_sign_in}")

        result = await ccc_service.ensure_agent_online(auto_sign_in=auto_sign_in)

        return result

    except Exception as e:
        logger.error(f"确保坐席在线失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"确保坐席在线失败: {str(e)}")
