"""
客户管理API路由
使用数据库存储替代内存存储
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import sys
import os

from models.database import get_db, Customer, CallRecord
from services.aliyun_ccc import CCCService

router = APIRouter(prefix="/api/customers", tags=["Customers"])

# 创建CCC服务实例（用于获取通话详情）
ccc_service = CCCService()


class CustomerCreate(BaseModel):
    """创建客户请求"""
    name: str
    phone: str
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    """更新客户请求"""
    name: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class CustomerResponse(BaseModel):
    """客户响应"""
    id: str
    name: str
    phone: str
    notes: Optional[str] = None
    created_at: str
    updated_at: str


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(db: Session = Depends(get_db)):
    """
    获取客户列表

    Returns:
        客户列表
    """
    try:
        # 从数据库查询所有客户，按创建时间倒序排序
        customers = db.query(Customer).order_by(Customer.created_at.desc()).all()
        return [customer.to_dict() for customer in customers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取客户列表失败: {str(e)}")


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """
    获取客户详情

    Args:
        customer_id: 客户ID

    Returns:
        客户详情
    """
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="客户不存在")
        return customer.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取客户失败: {str(e)}")


@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """
    创建客户

    Args:
        customer: 客户信息

    Returns:
        创建的客户
    """
    try:
        # 检查手机号是否已存在
        existing = db.query(Customer).filter(Customer.phone == customer.phone).first()
        if existing:
            raise HTTPException(status_code=400, detail="手机号已存在")

        # 创建新客户
        new_customer = Customer(
            id=str(uuid.uuid4()),
            name=customer.name,
            phone=customer.phone,
            notes=customer.notes,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)

        return new_customer.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建客户失败: {str(e)}")


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: str, customer: CustomerUpdate, db: Session = Depends(get_db)):
    """
    更新客户

    Args:
        customer_id: 客户ID
        customer: 更新信息

    Returns:
        更新后的客户
    """
    try:
        existing = db.query(Customer).filter(Customer.id == customer_id).first()
        if not existing:
            raise HTTPException(status_code=404, detail="客户不存在")

        # 更新字段
        if customer.name is not None:
            existing.name = customer.name
        if customer.phone is not None:
            # 检查新手机号是否与其他客户冲突
            conflict = db.query(Customer).filter(
                Customer.id != customer_id,
                Customer.phone == customer.phone
            ).first()
            if conflict:
                raise HTTPException(status_code=400, detail="手机号已被其他客户使用")
            existing.phone = customer.phone
        if customer.notes is not None:
            existing.notes = customer.notes

        existing.updated_at = datetime.now()

        db.commit()
        db.refresh(existing)

        return existing.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新客户失败: {str(e)}")


@router.delete("/{customer_id}")
async def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    """
    删除客户

    Args:
        customer_id: 客户ID

    Returns:
        删除结果
    """
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="客户不存在")

        db.delete(customer)
        db.commit()

        return {"message": "删除成功", "customer_id": customer_id}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除客户失败: {str(e)}")


@router.get("/{customer_id}/call-records")
async def get_customer_call_records(customer_id: str, db: Session = Depends(get_db)):
    """
    获取客户的通话记录

    Args:
        customer_id: 客户ID

    Returns:
        通话记录列表
    """
    try:
        # 检查客户是否存在
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="客户不存在")

        # 先查询数据库中的通话记录
        call_records = db.query(CallRecord).filter(
            CallRecord.customer_id == customer_id
        ).order_by(CallRecord.created_at.desc()).all()

        # 转换为字典列表
        records_dict = []
        for record in call_records:
            record_dict = record.to_dict()

            # 如果有contact_id，尝试从CCC API获取完整的通话详情
            if record.contact_id and ccc_service.client:
                try:
                    ccc_detail = await ccc_service.get_call_detail(record.contact_id)
                    if ccc_detail:
                        # 更新通话记录信息
                        detail_dict = ccc_detail.to_map() if hasattr(ccc_detail, 'to_map') else {}
                        if detail_dict:
                            record_dict['duration'] = detail_dict.get('CallDuration', record_dict.get('duration', 0))
                            record_dict['status'] = detail_dict.get('ContactDisposition', record_dict.get('status', 'unknown'))
                            record_dict['recording_url'] = f"/api/ccc/recording/{record.contact_id}" if detail_dict.get('RecordingReady', False) else None
                            if detail_dict.get('StartTime'):
                                record_dict['started_at'] = detail_dict.get('StartTime')
                except Exception as ccc_error:
                    # CCC API调用失败不影响返回
                    pass

            records_dict.append(record_dict)

        # 同时从CCC API获取最近的通话记录，根据手机号匹配
        if ccc_service.client:
            try:
                import time
                end_time = int(time.time() * 1000)
                start_time = end_time - 7 * 24 * 60 * 60 * 1000  # 最近7天

                ccc_records = await ccc_service.list_call_records(start_time, end_time)

                for ccc_record in ccc_records:
                    if hasattr(ccc_record, 'to_map'):
                        detail = ccc_record.to_map()
                    else:
                        continue

                    # 根据手机号匹配
                    called_number = detail.get('CalledNumber', '')
                    calling_number = detail.get('CallingNumber', '')
                    if called_number == customer.phone or calling_number == customer.phone:
                        # 检查是否已经存在于数据库中
                        contact_id = detail.get('ContactId', '')
                        exists = any(r.get('contact_id') == contact_id for r in records_dict)

                        if not exists:
                            # 添加CCC API的通话记录
                            records_dict.append({
                                'id': f"ccc-{contact_id}",
                                'customer_id': customer_id,
                                'callee_number': called_number or calling_number,
                                'calling_number': calling_number,
                                'call_type': detail.get('ContactType', 'Outbound'),  # 添加通话类型
                                'call_id': contact_id,
                                'contact_id': contact_id,
                                'status': detail.get('ContactDisposition', 'Unknown'),
                                'duration': detail.get('CallDuration', 0),
                                'recording_url': f"/api/ccc/recording/{contact_id}" if detail.get('RecordingReady', False) else None,
                                'started_at': detail.get('StartTime', ''),
                                'ended_at': detail.get('ReleaseTime', ''),
                                'created_at': detail.get('StartTime', ''),
                                'updated_at': detail.get('ReleaseTime', ''),
                            })
            except Exception as ccc_error:
                pass

        # 按时间倒序排序
        records_dict.sort(key=lambda x: str(x.get('started_at', '')), reverse=True)

        return {
            "customer_id": customer_id,
            "records": records_dict
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取通话记录失败: {str(e)}")


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """健康检查"""
    try:
        count = db.query(Customer).count()
        return {
            "status": "ok",
            "service": "customers",
            "count": count,
            "storage": "database"
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "customers",
            "error": str(e)
        }
