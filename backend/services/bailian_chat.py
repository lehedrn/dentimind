"""
百炼对话服务
使用dashscope SDK调用智能体应用API（支持session_id多轮对话）
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class BailianChatService:
    """百炼智能体对话服务（使用dashscope SDK）"""

    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.app_id = os.getenv("BAILIAN_APP_ID")

        if not self.api_key or not self.app_id:
            logger.warning("百炼API配置缺失，对话功能将不可用")

    async def chat(self, session_id: str, prompt: str) -> dict:
        """
        调用百炼智能体应用API（支持session_id多轮对话）

        Args:
            session_id: 会话ID（首次请求传空字符串，后续请求传入上次的session_id）
            prompt: 用户输入

        Returns:
            {
                "text": "AI回复内容",
                "session_id": "会话ID",
                "finish_reason": "stop"
            }
        """
        if not self.api_key or not self.app_id:
            raise Exception("百炼API配置缺失")

        logger.info(f"调用百炼API - session_id: {session_id}, prompt: {prompt[:50]}...")

        try:
            from dashscope import Application

            # 调用SDK
            if session_id:
                result = Application.call(
                    api_key=self.api_key,
                    app_id=self.app_id,
                    prompt=prompt,
                    session_id=session_id
                )
            else:
                result = Application.call(
                    api_key=self.api_key,
                    app_id=self.app_id,
                    prompt=prompt
                )

            # 检查响应状态
            if result.status_code == 200:
                return {
                    "text": result.output.text,
                    "session_id": result.output.session_id,
                    "finish_reason": "stop",
                }
            else:
                error_msg = result.message if hasattr(result, 'message') else 'Unknown error'
                logger.error(f"百炼API调用失败: {error_msg}")
                raise Exception(f"百炼API调用失败: {error_msg}")

        except Exception as e:
            logger.error(f"百炼API调用异常: {str(e)}")
            raise

    async def chat_new_session(self, prompt: str) -> dict:
        """
        创建新会话（首次请求，不传session_id）

        Args:
            prompt: 用户的第一条消息

        Returns:
            {
                "session_id": "新会话ID",
                "text": "AI回复内容"
            }
        """
        result = await self.chat("", prompt)
        return {
            "session_id": result["session_id"],
            "text": result["text"]
        }
