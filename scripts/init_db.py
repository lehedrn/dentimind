#!/usr/bin/env python3
"""
数据库初始化脚本
创建所有表并可选添加测试数据
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models.database import init_db, SessionLocal, Customer, CallRecord
from datetime import datetime
import uuid


def add_test_data():
    """添加测试数据"""
    db = SessionLocal()

    try:
        # 检查是否已有数据
        existing_count = db.query(Customer).count()
        if existing_count > 0:
            print(f"⚠ 数据库已有 {existing_count} 条客户记录，跳过测试数据添加")
            return

        print("📝 添加测试数据...")

        # 添加测试客户
        test_customers = [
            {
                "id": str(uuid.uuid4()),
                "name": "张三",
                "phone": "your-phone-number",
                "notes": "VIP客户，定期洗牙"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "李四",
                "phone": "13800138001",
                "notes": "需要补牙"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "王五",
                "phone": "13800138002",
                "notes": "首次咨询"
            }
        ]

        for customer_data in test_customers:
            customer = Customer(
                id=customer_data["id"],
                name=customer_data["name"],
                phone=customer_data["phone"],
                notes=customer_data["notes"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(customer)

        db.commit()
        print(f"✓ 成功添加 {len(test_customers)} 条测试客户记录")

        # 验证数据
        total_count = db.query(Customer).count()
        print(f"✓ 数据库共有 {total_count} 条客户记录")

    except Exception as e:
        db.rollback()
        print(f"✗ 添加测试数据失败: {str(e)}")
        raise
    finally:
        db.close()


def main():
    """主函数"""
    print("=" * 60)
    print("口腔医院AI客服系统 - 数据库初始化")
    print("=" * 60)

    try:
        # 初始化数据库（创建表）
        print("\n[1/2] 创建数据库表...")
        init_db()

        # 添加测试数据（可选）
        print("\n[2/2] 添加测试数据...")
        add_test_data()

        print("\n" + "=" * 60)
        print("✓ 数据库初始化完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 数据库初始化失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
