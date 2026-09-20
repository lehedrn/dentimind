#!/usr/bin/env python3
"""
获取CCC坐席列表
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from dotenv import load_dotenv
load_dotenv()

from alibabacloud_ccc20200701.client import Client
from alibabacloud_ccc20200701 import models
from alibabacloud_tea_openapi.models import Config


def get_agents():
    """获取坐席列表"""
    config = Config(
        access_key_id=os.getenv("ALIYUN_ACCESS_KEY_ID"),
        access_key_secret=os.getenv("ALIYUN_ACCESS_KEY_SECRET"),
        endpoint="ccc.cn-shanghai.aliyuncs.com"
    )
    client = Client(config)
    instance_id = os.getenv("CCC_INSTANCE_ID")

    print("=" * 60)
    print("CCC坐席列表")
    print("=" * 60)
    print(f"Instance ID: {instance_id}")
    print()

    try:
        # 尝试不同的API方法来获取坐席列表
        print("尝试获取坐席列表...")

        # 方法1: ListUsers - 列出用户
        try:
            request = models.ListUsersRequest(
                instance_id=instance_id,
                page_number=1,
                page_size=100
            )
            response = client.list_users(request)

            print(f"ListUsers响应: {response.body}")
            print()

            if response.body and response.body.data:
                users = response.body.data.list if hasattr(response.body.data, 'list') else []
                print(f"找到 {len(users)} 个用户:")
                print()

                for user in users:
                    print(f"用户对象: {user}")
                    print(f"用户ID: {user.user_id if hasattr(user, 'user_id') else 'N/A'}")
                    print(f"用户名: {user.login_name if hasattr(user, 'login_name') else 'N/A'}")
                    print(f"显示名: {user.display_name if hasattr(user, 'display_name') else 'N/A'}")
                    print(f"角色: {user.role_name if hasattr(user, 'role_name') else 'N/A'}")
                    print("-" * 60)

                # 查找 ztq1
                print("\n查找用户名 ztq1:")
                for user in users:
                    login_name = user.login_name if hasattr(user, 'login_name') else ''
                    if login_name == 'ztq1':
                        print(f"✅ 找到!")
                        print(f"用户ID: {user.user_id}")
                        print(f"用户名: {user.login_name}")
                        print(f"显示名: {user.display_name}")
                        return user.user_id

        except Exception as e:
            print(f"ListUsers失败: {str(e)}")
            import traceback
            traceback.print_exc()

        # 方法2: ListAgents - 列出坐席
        try:
            request = models.ListAgentsRequest(
                instance_id=instance_id,
                page_number=1,
                page_size=100
            )
            response = client.list_agents(request)

            if response.body and response.body.data:
                agents = response.body.data.list if hasattr(response.body.data, 'list') else []
                print(f"找到 {len(agents)} 个坐席:")
                print()

                for agent in agents:
                    print(f"坐席ID: {agent.agent_id if hasattr(agent, 'agent_id') else 'N/A'}")
                    print(f"用户名: {agent.login_name if hasattr(agent, 'login_name') else 'N/A'}")
                    print(f"显示名: {agent.display_name if hasattr(agent, 'display_name') else 'N/A'}")
                    print("-" * 60)

                # 查找 ztq1
                print("\n查找用户名 ztq1:")
                for agent in agents:
                    login_name = agent.login_name if hasattr(agent, 'login_name') else ''
                    if login_name == 'ztq1':
                        print(f"✅ 找到!")
                        print(f"坐席ID: {agent.agent_id}")
                        print(f"用户名: {agent.login_name}")
                        print(f"显示名: {agent.display_name}")
                        return agent.agent_id

        except Exception as e:
            print(f"ListAgents失败: {str(e)}")

        print("\n未找到用户名 ztq1 的坐席")
        return None

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    agent_id = get_agents()
    if agent_id:
        print(f"\n建议在 .env 中设置: CCC_USER_ID={agent_id}")
