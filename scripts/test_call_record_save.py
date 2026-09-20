#!/usr/bin/env python3
"""
测试通话记录自动保存逻辑
模拟外呼成功后的数据库操作
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models.database import SessionLocal, Customer, CallRecord
from datetime import datetime
import uuid

def test_auto_save_call_record():
    """测试通话记录自动保存"""
    db = SessionLocal()

    try:
        print("=" * 60)
        print("测试通话记录自动保存逻辑")
        print("=" * 60)

        # 模拟外呼的手机号
        test_phone = "13950481396"

        # 步骤1：根据手机号查找客户
        print(f"\n[1/4] 查找客户 - phone: {test_phone}")
        customer = db.query(Customer).filter(Customer.phone == test_phone).first()
        if customer:
            print(f"✓ 找到客户 - id: {customer.id}, name: {customer.name}")
        else:
            print(f"✗ 客户不存在，将自动创建")
            customer = Customer(
                id=str(uuid.uuid4()),
                name=f"客户{test_phone[-4:]}",
                phone=test_phone,
                notes="自动创建（来自外呼）",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)
            print(f"✓ 自动创建客户 - id: {customer.id}, name: {customer.name}")

        # 步骤2：创建通话记录
        print(f"\n[2/4] 创建通话记录")
        mock_call_id = f"test-call-{uuid.uuid4().hex[:8]}"
        call_record = CallRecord(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            callee_number=test_phone,
            call_id=mock_call_id,
            contact_id=f"test-contact-{uuid.uuid4().hex[:8]}",
            status="initiated",
            duration=0,
            started_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(call_record)
        db.commit()
        db.refresh(call_record)
        print(f"✓ 创建通话记录成功 - id: {call_record.id}, call_id: {call_record.call_id}")

        # 步骤3：验证关联关系
        print(f"\n[3/4] 验证关联关系")
        customer_with_records = db.query(Customer).filter(Customer.id == customer.id).first()
        record_count = len(customer_with_records.call_records)
        print(f"✓ 客户通话记录数量: {record_count}")

        # 步骤4：查询客户的通话记录
        print(f"\n[4/4] 查询客户通话记录")
        records = db.query(CallRecord).filter(
            CallRecord.customer_id == customer.id
        ).order_by(CallRecord.created_at.desc()).all()

        print(f"✓ 找到 {len(records)} 条通话记录")
        for i, record in enumerate(records, 1):
            print(f"  [{i}] call_id: {record.call_id}, status: {record.status}, " +
                  f"callee: {record.callee_number}")

        print("\n" + "=" * 60)
        print("✓ 测试通过！通话记录自动保存逻辑正常工作")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_auto_save_call_record()
