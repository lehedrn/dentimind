#!/usr/bin/env python3
"""
测试百炼对话功能（流式API）
"""
import os
import sys
import asyncio
import httpx

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from dotenv import load_dotenv
load_dotenv()


async def test_chat():
    """测试对话功能"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    agent_id = os.getenv("BAILIAN_APP_ID")
    api_endpoint = "https://ws-g363nh1vzucbq989.cn-beijing.maas.aliyuncs.com/api/v2/apps/knowledge/chat"

    print("=" * 60)
    print("百炼对话功能测试（流式API）")
    print("=" * 60)
    print(f"Agent ID: {agent_id}")
    print(f"API Key: {api_key[:20]}...")
    print(f"Endpoint: {api_endpoint}")
    print()

    if not api_key or not agent_id:
        print("❌ 错误：缺少API配置")
        print("请检查 .env 文件中的 BAILIAN_APP_ID 和 DASHSCOPE_API_KEY")
        return False

    try:
        print("测试1：简单问题")
        print("-" * 60)
        question1 = "洗牙多少钱？"
        print(f"问题：{question1}")
        print("回答：", end="", flush=True)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": question1
                    }
                ]
            },
            "parameters": {
                "agent_options": {
                    "agent_id": agent_id
                }
            },
            "stream": True  # 必须使用流式
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                api_endpoint,
                headers=headers,
                json=payload
            ) as response:
                if response.status_code != 200:
                    print(f"\n❌ API调用失败: {response.status_code}")
                    await response.aread()
                    print(f"响应: {response.text}")
                    return False

                full_response = ""
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str and data_str != "[DONE]":
                            try:
                                import json
                                data = json.loads(data_str)
                                if "output" in data and "choices" in data["output"]:
                                    for choice in data["output"]["choices"]:
                                        if "message" in choice and "content" in choice["message"]:
                                            content = choice["message"]["content"]
                                            print(content, end="", flush=True)
                                            full_response += content
                            except Exception as e:
                                pass

                print("\n")

        print(f"\n完整回答长度: {len(full_response)} 字符")
        print()

        print("测试2：另一个问题")
        print("-" * 60)
        question2 = "种植牙疼不疼？"
        print(f"问题：{question2}")
        print("回答：", end="", flush=True)

        payload["input"]["messages"][0]["content"] = question2

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                api_endpoint,
                headers=headers,
                json=payload
            ) as response:
                if response.status_code != 200:
                    print(f"\n❌ API调用失败: {response.status_code}")
                    await response.aread()
                    print(f"响应: {response.text}")
                    return False

                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str and data_str != "[DONE]":
                            try:
                                import json
                                data = json.loads(data_str)
                                if "output" in data and "choices" in data["output"]:
                                    for choice in data["output"]["choices"]:
                                        if "message" in choice and "content" in choice["message"]:
                                            content = choice["message"]["content"]
                                            print(content, end="", flush=True)
                            except Exception as e:
                                pass

                print("\n")

        print("=" * 60)
        print("✅ 测试通过！百炼对话功能正常")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_chat())
    sys.exit(0 if success else 1)
