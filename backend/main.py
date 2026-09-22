"""
FastAPI主入口
"""
import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import time

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from logging_config import LogConfig, setup_uvicorn_logging
from routers import chat, ccc, customers, webhook, ccc_proxy, softphone
from models.database import init_db

# 配置日志系统
LogConfig.setup_logging()

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="口腔医院AI客服系统",
    description="AI客服系统API - 对接阿里云CCC和百炼",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# HTTP请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求"""
    start_time = time.time()

    # 获取请求信息
    method = request.method
    url = str(request.url)
    client_ip = request.client.host if request.client else "unknown"

    # 记录请求开始
    logger.debug(f"→ {method} {url} - 客户端: {client_ip}")

    try:
        # 处理请求
        response = await call_next(request)

        # 计算处理时间
        process_time = time.time() - start_time

        # 记录响应
        logger.info(
            f"← {method} {url} - "
            f"状态: {response.status_code} - "
            f"耗时: {process_time:.3f}s - "
            f"客户端: {client_ip}"
        )

        return response

    except Exception as e:
        # 记录异常
        process_time = time.time() - start_time
        logger.error(
            f"✗ {method} {url} - "
            f"异常: {str(e)} - "
            f"耗时: {process_time:.3f}s - "
            f"客户端: {client_ip}",
            exc_info=True
        )
        raise

# 注册路由
app.include_router(chat.router)
app.include_router(ccc.router)
app.include_router(customers.router)
app.include_router(webhook.router)
app.include_router(ccc_proxy.router)
app.include_router(softphone.router)


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("=" * 80)
    logger.info("口腔医院AI客服系统启动中...")
    logger.info("=" * 80)

    # 创建日志目录
    log_dir = Path("./logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"日志目录: {log_dir.absolute()}")

    # 初始化数据库
    try:
        logger.info("初始化数据库...")
        init_db()
        logger.info("✓ 数据库初始化成功")
    except Exception as e:
        logger.error(f"✗ 数据库初始化失败: {e}", exc_info=True)
        raise

    # 验证配置
    try:
        logger.info("验证配置...")
        Config.validate()
        logger.info("✓ 配置验证通过")
        logger.info(f"  - 百炼APP_ID: {Config.BAILIAN_APP_ID[:8]}...")
        logger.info(f"  - CCC实例ID: {Config.CCC_INSTANCE_ID}")
    except ValueError as e:
        logger.warning(f"⚠ 配置验证失败: {e}")

    # 显示服务信息
    ssl_cert = os.getenv("SSL_CERT_FILE")
    ssl_key = os.getenv("SSL_KEY_FILE")
    protocol = "https" if (ssl_cert and ssl_key) else "http"
    base_url = f"{protocol}://{Config.API_HOST}:{Config.API_PORT}"

    logger.info("=" * 80)
    logger.info(f"✓ 服务启动成功!")
    logger.info(f"  - 协议: {protocol.upper()} {'(HTTPS 已启用)' if protocol == 'https' else '(HTTP)'}")
    logger.info(f"  - 访问地址: {base_url}")
    logger.info(f"  - API文档: {base_url}/docs")
    logger.info(f"  - 文本客服: {base_url}/chat")
    logger.info(f"  - 外呼管理: {base_url}/outbound")
    logger.info(f"  - 客户管理: {base_url}/customers")
    logger.info(f"  - 软电话: {base_url}/softphone")
    logger.info(f"  - CCC工作台: {base_url}/ccc-workbench")
    logger.info("=" * 80)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "口腔医院AI客服系统API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "service": "dental-ai-system"
    }


@app.get("/api/config")
async def get_config():
    """获取前端配置（不包含敏感信息）"""
    return {
        "ccc_instance_id": Config.CCC_INSTANCE_ID,
        "ccc_region_id": Config.CCC_REGION_ID,
        "ccc_user_id": Config.CCC_USER_ID,
        "ccc_device_id": Config.CCC_DEVICE_ID,
        "white_list_phone": os.getenv("WHITE_LIST_PHONE", ""),
        "api_port": Config.API_PORT,
        "debug": Config.DEBUG
    }


# 挂载静态文件（前端页面）
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/chat")
    async def chat_page():
        """文本客服页面"""
        return FileResponse(frontend_dir / "chat-widget.html")

    @app.get("/outbound")
    async def outbound_page():
        """外呼管理页面"""
        return FileResponse(frontend_dir / "outbound.html")

    @app.get("/customers")
    async def customers_page():
        """客户管理页面"""
        return FileResponse(frontend_dir / "customers.html")

    @app.get("/softphone")
    async def softphone_page():
        """软电话页面"""
        return FileResponse(frontend_dir / "softphone.html")

    @app.get("/softphone-test")
    async def softphone_test_page():
        """软电话调试页面"""
        return FileResponse(frontend_dir / "softphone-test.html")

    @app.get("/ccc-workbench")
    async def ccc_workbench_page():
        """CCC 工作台页面（iframe 嵌入）"""
        return FileResponse(frontend_dir / "ccc-workbench.html")


if __name__ == "__main__":
    import uvicorn
    ssl_cert = os.getenv("SSL_CERT_FILE")
    ssl_key = os.getenv("SSL_KEY_FILE")
    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.DEBUG,
        ssl_certfile=ssl_cert,
        ssl_keyfile=ssl_key,
    )
