#!/usr/bin/env python3
"""
使用list_users API获取所有用户
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from dotenv import load_dotenv
load_dotenv()

from alibabacloud_ccc20200701.client import Client
from alibabacloud_ccc20200701 import models
from alibabacloud_tea_openapi.models import Config


def list_all_users():
    """列出所有用户"""
    config = Config(
        access_key_id=os.getenv("ALIYUN_ACCESS_KEY_ID"),
        access_key_secret=os.getenv("ALIYUN_ACCESS_KEY_SECRET"),
        endpoint="ccc.cn-shanghai.aliyuncs.com"
    )
    client = Client(config)
    instance_id = os.getenv("CCC_INSTANCE_ID")

    print("=" * 60)
    print("列出所有CCC用户")
    print("=" * 60)
    print(f"Instance ID: {instance_id}")
    print()

    try:
        # 使用正确的参数调用list_users
        request = models.ListUsersRequest(
            instance_id=instance_id,
            page_number=1,
            page_size=100
        )

        print("调用 ListUsers API...")
        response = client.list_users(request)

        print(f"响应状态: {response.body.code if hasattr(response.body, 'code') else 'N/A'}")
        print(f"响应消息: {response.body.message if hasattr(response.body, 'message') else 'N/A'}")
        print()

        if response.body and hasattr(response.body, 'data') and response.body.data:
            data = response.body.data
            print(f"Data类型: {type(data)}")

            # 尝试获取用户列表
            if hasattr(data, 'list'):
                users = data.list
                print(f"找到 {len(users)} 个用户:")
                print()

                for i, user in enumerate(users, 1):
                    print(f"--- 用户 {i} ---")
                    print(f"  UserId: {user.user_id if hasattr(user, 'user_id') else 'N/A'}")
                    print(f"  LoginName: {user.login_name if hasattr(user, 'login_name') else 'N/A'}")
                    print(f"  DisplayName: {user.display_name if hasattr(user, 'display_name') else 'N/A'}")
                    print(f"  Mobile: {user.mobile if hasattr(user, 'mobile') else 'N/A'}")
                    print(f"  RoleName: {user.role_name if hasattr(user, 'role_name') else 'N/A'}")
                    print()

                    # 查找 ztq1
                    login_name = user.login_name if hasattr(user, 'login_name') else ''
                    if 'ztq1' in str(login_name).lower():
                        print(f"✅ 找到 ztq1!")
                        print(f"   UserId: {user.user_id}")
                        return user.user_id

            else:
                print(f"Data没有list属性")
                print(f"Data内容: {data}")
        else:
            print("响应中没有data")
            print(f"完整响应: {response.body}")

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

    return None


if __name__ == "__main__":
    user_id = list_all_users()
    if user_id:
        print(f"\n✅ 找到坐席ID: {user_id}")
        print(f"建议在 .env 中设置: CCC_USER_ID={user_id}")
    else:
        print("\n❌ 未找到坐席ID")
