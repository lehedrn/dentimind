"""
配置管理模块
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置"""

    # 阿里云CCC配置
    CCC_INSTANCE_ID = os.getenv("CCC_INSTANCE_ID")
    ALIYUN_ACCESS_KEY_ID = os.getenv("ALIYUN_ACCESS_KEY_ID")
    ALIYUN_ACCESS_KEY_SECRET = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
    CCC_CALLER_NUMBER = os.getenv("CCC_CALLER_NUMBER")
    CCC_USER_ID = os.getenv("CCC_USER_ID")
    CCC_DEVICE_ID = os.getenv("CCC_DEVICE_ID", "device")
    CCC_REGION_ID = os.getenv("CCC_REGION_ID", "cn-shanghai")

    # 阿里云百炼配置
    BAILIAN_APP_ID = os.getenv("BAILIAN_APP_ID")
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

    # 数据库配置
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dental_ai.db")
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))

    # 服务配置
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # CORS配置
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "./logs/app.log")

    # Webhook配置
    CCC_WEBHOOK_URL = os.getenv("CCC_WEBHOOK_URL")

    # 其他配置
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Shanghai")

    @classmethod
    def validate(cls):
        """验证必需的配置"""
        missing = []

        if not cls.BAILIAN_APP_ID:
            missing.append("BAILIAN_APP_ID")
        if not cls.DASHSCOPE_API_KEY:
            missing.append("DASHSCOPE_API_KEY")
        if not cls.CCC_INSTANCE_ID:
            missing.append("CCC_INSTANCE_ID")
        if not cls.ALIYUN_ACCESS_KEY_ID:
            missing.append("ALIYUN_ACCESS_KEY_ID")
        if not cls.ALIYUN_ACCESS_KEY_SECRET:
            missing.append("ALIYUN_ACCESS_KEY_SECRET")

        if missing:
            raise ValueError(f"缺少必需的环境变量配置: {', '.join(missing)}")

        return True
