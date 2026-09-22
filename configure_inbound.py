#!/usr/bin/env python3
"""
CCC 呼入配置工具
通过 API 配置呼入路由和 Webhook
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from dotenv import load_dotenv
load_dotenv()

from services.aliyun_ccc import CCCService
from alibabacloud_ccc20200701 import models


def configure_inbound_route(phone_number: str, target_user_id: str = None):
    """
    配置呼入路由

    注意:CCC API 可能不支持直接创建路由,需要先确认 API 能力
    """
    ccc = CCCService()
    if not ccc.client:
        print("❌ CCC 服务未初始化")
        return False

    print(f"尝试配置呼入路由...")
    print(f"  号码: {phone_number}")
    print(f"  目标坐席: {target_user_id or os.getenv('CCC_USER_ID')}")
    print()

    # 尝试查询现有路由(如果 API 支持)
    try:
        # 注意:这个 API 可能不存在,取决于 CCC 版本
        # 常见的相关 API:
        # - ListInboundPhoneNumbers
        # - GetInboundConfig
        # - ListContactFlows

        print("【检查现有路由配置】")

        # 尝试 1: ListInboundPhoneNumbers
        try:
            request = models.ListInboundPhoneNumbersRequest(
                instance_id=ccc.instance_id,
                page_number=1,
                page_size=100
            )
            response = ccc.client.list_inbound_phone_numbers(request)
            print(f"  ✓ 查询呼入号码配置成功")
            if response.body and response.body.data:
                numbers = response.body.data.list or []
                for num in numbers:
                    print(f"    - {num}")
        except AttributeError:
            print(f"  ⚠ API 不支持: ListInboundPhoneNumbers")
        except Exception as e:
            print(f"  ⚠ 查询失败: {e}")

        # 尝试 2: ListContactFlows (IVR 流程)
        try:
            request = models.ListContactFlowsRequest(
                instance_id=ccc.instance_id,
                page_number=1,
                page_size=100
            )
            response = ccc.client.list_contact_flows(request)
            print(f"  ✓ 查询联系流程成功")
            if response.body and response.body.data:
                flows = response.body.data.list or []
                for flow in flows:
                    print(f"    - {flow}")
        except AttributeError:
            print(f"  ⚠ API 不支持: ListContactFlows")
        except Exception as e:
            print(f"  ⚠ 查询失败: {e}")

    except Exception as e:
        print(f"❌ 查询路由配置失败: {e}")

    print()
    print("【建议】")
    print("  CCC API 可能不直接支持创建呼入路由")
    print("  建议通过控制台配置:")
    print("  1. 登录: https://ccc.console.aliyun.com/")
    print("  2. 左侧菜单: 呼叫中心配置 → 呼入管理")
    print("  3. 创建路由规则,绑定号码")
    print()


def check_webhook_config():
    """检查 Webhook 配置"""
    ccc = CCCService()
    if not ccc.client:
        print("❌ CCC 服务未初始化")
        return

    print("【检查 Webhook/事件订阅配置】")

    # 尝试查询事件订阅(如果 API 支持)
    try:
        # CCC 可能使用 EventBridge 或自己的事件订阅系统
        # 常见 API:
        # - ListEventSubscriptions
        # - GetWebhookConfig

        try:
            request = models.ListEventSubscriptionsRequest(
                instance_id=ccc.instance_id
            )
            response = ccc.client.list_event_subscriptions(request)
            print(f"  ✓ 查询事件订阅成功")
            if response.body and response.body.data:
                subs = response.body.data
                print(f"    {subs}")
        except AttributeError:
            print(f"  ⚠ API 不支持: ListEventSubscriptions")
        except Exception as e:
            print(f"  ⚠ 查询失败: {e}")

    except Exception as e:
        print(f"❌ 查询失败: {e}")

    print()
    print("【Webhook 配置建议】")
    print("  方案 1: CCC 控制台配置")
    print("    - 设置 → Webhook 或 事件订阅")
    print()
    print("  方案 2: 使用阿里云 EventBridge(推荐)")
    print("    - 开通 EventBridge 服务")
    print("    - 创建事件规则:CCC 通话事件 → 你的 Webhook URL")
    print("    - 优势:更可靠,支持重试")
    print()
    print("  方案 3: 轮询 CCC API(备选)")
    print("    - 定时调用 ListRecentCalls 查询最近通话")
    print("    - 缺点:不是实时的,有延迟")
    print()


def main():
    print("=" * 80)
    print("CCC 呼入配置工具")
    print("=" * 80)
    print()

    phone_number = "057123679672"

    # 1. 检查路由配置
    configure_inbound_route(phone_number)

    # 2. 检查 Webhook 配置
    check_webhook_config()

    print("=" * 80)
    print("【下一步】")
    print("=" * 80)
    print()
    print("1. 登录 CCC 控制台: https://ccc.console.aliyun.com/")
    print("2. 选择实例: your-ccc-instance-id")
    print("3. 配置呼入路由(绑定号码 057123679672)")
    print("4. 配置 Webhook(通话结束回调)")
    print()
    print("如果在控制台找不到配置项,请告诉我具体的菜单结构,")
    print("我可以帮你进一步分析。")
    print()


if __name__ == "__main__":
    main()
