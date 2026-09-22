"""
文本客服API路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.bailian_chat import BailianChatService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    """对话请求"""
    session_id: str
    message: str


class ChatResponse(BaseModel):
    """对话响应"""
    session_id: str
    reply: str
    finish_reason: str


chat_service = BailianChatService()


@router.post("/message", response_model=ChatResponse)
async def send_message(req: ChatRequest):
    """
    发送消息给AI客服（多轮对话）

    Args:
        req: 包含session_id和message的请求

    Returns:
        AI回复内容
    """
    try:
        logger.info(f"收到对话请求 - session_id: {req.session_id}, message: {req.message[:50]}...")
        logger.debug(f"完整请求内容: session_id={req.session_id}, message={req.message}")

        response = await chat_service.chat(req.session_id, req.message)

        logger.info(f"对话响应成功 - session_id: {response['session_id']}, reply长度: {len(response['text'])}")
        logger.debug(f"完整响应内容: {response}")

        return ChatResponse(
            session_id=response["session_id"],
            reply=response["text"],
            finish_reason=response["finish_reason"]
        )

    except Exception as e:
        logger.error(f"对话处理失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"对话处理失败: {str(e)}")


@router.post("/new-session")
async def new_chat_session(message: str):
    """
    开始新的对话会话

    Args:
        message: 用户的第一条消息

    Returns:
        新会话的session_id和AI回复
    """
    try:
        logger.info(f"创建新会话 - message: {message[:50]}...")

        response = await chat_service.chat_new_session(message)

        return {
            "session_id": response["session_id"],
            "reply": response["text"]
        }

    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    健康检查
    """
    return {
        "status": "ok",
        "service": "chat",
        "configured": bool(chat_service.api_key and chat_service.app_id)
    }
