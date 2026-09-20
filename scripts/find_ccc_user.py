#!/usr/bin/env python3
"""
尝试获取CCC坐席信息 - 详细版
"""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from dotenv import load_dotenv
load_dotenv()

from alibabacloud_ccc20200701.client import Client
from alibabacloud_ccc20200701 import models
from alibabacloud_tea_openapi.models import Config


def try_get_user_info():
    """尝试多种方式获取用户信息"""
    config = Config(
        access_key_id=os.getenv("ALIYUN_ACCESS_KEY_ID"),
        access_key_secret=os.getenv("ALIYUN_ACCESS_KEY_SECRET"),
        endpoint="ccc.cn-shanghai.aliyuncs.com"
    )
    client = Client(config)
    instance_id = os.getenv("CCC_INSTANCE_ID")

    print("=" * 60)
    print("尝试获取CCC坐席信息")
    print("=" * 60)
    print(f"Instance ID: {instance_id}")
    print()

    # 尝试1: 使用GetUser方法
    print("尝试1: GetUser - 获取指定用户")
    try:
        # 尝试常见的用户ID格式
        test_user_ids = [
            "ztq1",
            "user-ztq1",
            "agent-ztq1",
            "207560989376770516",
        ]

        for user_id in test_user_ids:
            try:
                print(f"  尝试 user_id: {user_id}")
                request = models.GetUserRequest(
                    instance_id=instance_id,
                    user_id=user_id
                )
                response = client.get_user(request)
                print(f"  ✅ 成功! 响应: {response.body}")

                if response.body and response.body.data:
                    user = response.body.data
                    print(f"\n用户详情:")
                    print(f"  用户ID: {user.user_id if hasattr(user, 'user_id') else 'N/A'}")
                    print(f"  用户名: {user.login_name if hasattr(user, 'login_name') else 'N/A'}")
                    print(f"  显示名: {user.display_name if hasattr(user, 'display_name') else 'N/A'}")
                    return user.user_id

            except Exception as e:
                print(f"  ❌ 失败: {str(e)[:100]}")

    except Exception as e:
        print(f"GetUser方法失败: {str(e)}")

    # 尝试2: 使用ListPhoneNumbers获取实例信息
    print("\n尝试2: ListPhoneNumbers - 获取号码列表（可能包含用户信息）")
    try:
        request = models.ListPhoneNumbersRequest(
            instance_id=instance_id
        )
        response = client.list_phone_numbers(request)
        print(f"响应: {response.body}")

        if response.body and response.body.data:
            numbers = response.body.data.list if hasattr(response.body.data, 'list') else []
            print(f"找到 {len(numbers)} 个号码")
            for num in numbers:
                print(f"号码: {num}")

    except Exception as e:
        print(f"ListPhoneNumbers失败: {str(e)[:100]}")

    # 尝试3: 获取实例信息
    print("\n尝试3: GetInstance - 获取实例信息")
    try:
        request = models.GetInstanceRequest(
            instance_id=instance_id
        )
        response = client.get_instance(request)
        print(f"响应: {response.body}")

    except Exception as e:
        print(f"GetInstance失败: {str(e)[:100]}")

    # 尝试4: 使用通用方法列出所有可能的API
    print("\n尝试4: 检查可用的API方法")
    try:
        methods = [m for m in dir(client) if not m.startswith('_') and callable(getattr(client, m))]
        print(f"可用的client方法: {len(methods)}")
        relevant_methods = [m for m in methods if 'user' in m.lower() or 'agent' in m.lower() or 'list' in m.lower()]
        print(f"相关方法: {relevant_methods}")
    except Exception as e:
        print(f"检查方法失败: {str(e)}")

    return None


if __name__ == "__main__":
    user_id = try_get_user_info()
    if user_id:
        print(f"\n✅ 找到坐席ID: {user_id}")
        print(f"建议在 .env 中设置: CCC_USER_ID={user_id}")
    else:
        print("\n❌ 未找到坐席ID")
        print("建议手动在CCC控制台查看")
