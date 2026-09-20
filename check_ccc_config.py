#!/usr/bin/env python3
"""
查询 CCC 配置状态
帮助检查呼入功能的配置情况
"""
import os
import sys
from pathlib import Path

# 添加 backend 到路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from dotenv import load_dotenv
load_dotenv()

from services.aliyun_ccc import CCCService
from alibabacloud_ccc20200701 import models


def check_config():
    """检查配置"""
    print("=" * 80)
    print("阿里云 CCC 配置检查")
    print("=" * 80)
    print()

    # 检查环境变量
    print("【1. 环境变量检查】")
    instance_id = os.getenv("CCC_INSTANCE_ID")
    caller_number = os.getenv("CCC_CALLER_NUMBER")
    user_id = os.getenv("CCC_USER_ID")
    access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")

    print(f"  CCC_INSTANCE_ID: {instance_id or '❌ 未配置'}")
    print(f"  CCC_CALLER_NUMBER: {caller_number or '❌ 未配置'}")
    print(f"  CCC_USER_ID: {user_id or '❌ 未配置'}")
    print(f"  ALIYUN_ACCESS_KEY_ID: {access_key_id[:10] + '...' if access_key_id else '❌ 未配置'}")
    print()

    if not all([instance_id, caller_number, user_id, access_key_id]):
        print("❌ 环境变量配置不完整,请检查 .env 文件")
        return

    # 初始化 CCC 服务
    print("【2. CCC 服务初始化】")
    ccc = CCCService()
    if not ccc.client:
        print("❌ CCC 服务初始化失败")
        return
    print(f"✓ CCC 服务初始化成功 - Instance ID: {ccc.instance_id}")
    print()

    # 查询坐席状态
    print("【3. 坐席状态】")
    try:
        agent_status = ccc.check_agent_status()
        status_icon = "✓" if agent_status["is_online"] else "⚠"
        print(f"  {status_icon} 坐席状态: {agent_status['agent_status']}")
        print(f"    用户 ID: {agent_status['user_id']}")
        if not agent_status["is_online"]:
            print("    ⚠ 坐席不在线,需要签到才能接听电话")
            print("    调用: curl -X POST http://localhost:8000/api/ccc/agent/sign-in")
    except Exception as e:
        print(f"  ❌ 查询坐席状态失败: {e}")
    print()

    # 查询号码列表
    print("【4. 号码列表】")
    try:
        request = models.ListPhoneNumbersRequest(
            instance_id=ccc.instance_id,
            page_number=1,
            page_size=100
        )
        response = ccc.client.list_phone_numbers(request)

        if response.body and response.body.data:
            numbers = response.body.data.list or []
            print(f"  ✓ 找到 {len(numbers)} 个号码:")
            for num in numbers:
                number = getattr(num, 'number', 'Unknown')
                usage = getattr(num, 'usage', 'Unknown')
                province = getattr(num, 'province', '')
                city = getattr(num, 'city', '')
                print(f"    - {number}")
                print(f"      用途: {usage}")
                if province or city:
                    print(f"      归属地: {province} {city}")

                # 检查是否是用户提到的号码
                if '057123679672' in str(number) or '66905712367967212' in str(number):
                    print(f"      ⭐ 这是你提到的号码")
        else:
            print("  ⚠ 未找到号码,或查询失败")
            print("    可能原因:")
            print("    1. 实例下没有号码")
            print("    2. 号码未绑定到该实例")
    except Exception as e:
        print(f"  ❌ 查询号码失败: {e}")
    print()

    # 查询技能组
    print("【5. 技能组列表】")
    try:
        request = models.ListSkillGroupsRequest(
            instance_id=ccc.instance_id,
            page_number=1,
            page_size=100
        )
        response = ccc.client.list_skill_groups(request)

        if response.body and response.body.data:
            groups = response.body.data.list or []
            print(f"  ✓ 找到 {len(groups)} 个技能组:")
            for group in groups:
                group_id = getattr(group, 'skill_group_id', 'Unknown')
                name = getattr(group, 'name', 'Unknown')
                media_type = getattr(group, 'media_type', 'Unknown')
                print(f"    - {name}")
                print(f"      ID: {group_id}")
                print(f"      媒体类型: {media_type}")
        else:
            print("  ⚠ 未找到技能组")
    except Exception as e:
        print(f"  ❌ 查询技能组失败: {e}")
    print()

    # 查询坐席列表
    print("【6. 坐席列表】")
    try:
        request = models.ListUsersRequest(
            instance_id=ccc.instance_id,
            page_number=1,
            page_size=100,
            user_id=user_id
        )
        response = ccc.client.list_users(request)

        if response.body and response.body.data:
            users = response.body.data.list or []
            print(f"  ✓ 找到 {len(users)} 个坐席:")
            for user in users:
                uid = getattr(user, 'user_id', 'Unknown')
                display_name = getattr(user, 'display_name', 'Unknown')
                extension = getattr(user, 'extension', 'Unknown')
                print(f"    - {display_name}")
                print(f"      用户 ID: {uid}")
                print(f"      分机号: {extension}")
        else:
            print("  ⚠ 未找到坐席")
    except Exception as e:
        print(f"  ❌ 查询坐席失败: {e}")
    print()

    # 查询呼入路由(如果 API 支持)
    print("【7. 呼入路由配置】")
    print("  ⚠ CCC API 可能不直接支持查询路由配置")
    print("  📋 请在 CCC 控制台检查:")
    print("     1. 登录: https://ccc.console.aliyun.com/")
    print("     2. 选择实例: demo-1767693362317534")
    print("     3. 左侧菜单: 呼叫中心配置 → 呼入管理 → 呼入路由")
    print("     4. 检查是否有路由规则:")
    print("        - 绑定号码: 057123679672")
    print("        - 目标技能组/坐席: 智天气@demo-1767693362317534")
    print()

    # Webhook 配置
    print("【8. Webhook 配置】")
    print("  ⚠ CCC API 可能不直接支持查询 Webhook 配置")
    print("  📋 请在 CCC 控制台检查:")
    print("     1. 登录: https://ccc.console.aliyun.com/")
    print("     2. 选择实例: demo-1767693362317534")
    print("     3. 左侧菜单: 设置 → Webhook 或 事件订阅")
    print("     4. 添加 Webhook:")
    print("        - 事件类型: 通话结束 (CallEnded)")
    print("        - URL: http://<你的公网地址>/api/webhook/ccc/call-ended")
    print("        - 注意: URL 必须公网可访问")
    print()

    # 总结
    print("=" * 80)
    print("【下一步操作建议】")
    print("=" * 80)
    print()
    print("1. 确认号码绑定:")
    print("   - 检查上面的号码列表,确认 057123679672 已绑定到实例")
    print("   - 如果没有,需要在 CCC 控制台绑定号码")
    print()
    print("2. 配置呼入路由:")
    print("   - 在 CCC 控制台 → 呼入管理 → 呼入路由")
    print("   - 创建路由规则,绑定号码 057123679672")
    print("   - 设置目标技能组或坐席")
    print()
    print("3. 配置 Webhook:")
    print("   - 在 CCC 控制台 → 设置 → Webhook")
    print("   - 添加通话结束事件的回调 URL")
    print("   - URL 需要公网可访问(使用 ngrok 或部署到公网)")
    print()
    print("4. 测试呼入:")
    print("   - 确保坐席在线: curl -X POST http://localhost:8000/api/ccc/agent/sign-in")
    print("   - 用测试手机拨打 057123679672")
    print("   - 查看日志: tail -f backend/logs/app.log | grep Webhook")
    print()


if __name__ == "__main__":
    check_config()
