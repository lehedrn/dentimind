"""
日志配置模块
提供统一的日志管理
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path


class LogConfig:
    """日志配置"""

    LOG_DIR = os.getenv("LOG_DIR", "./logs")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")  # 开发阶段使用DEBUG
    LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # 日志文件配置
    APP_LOG_FILE = "app.log"
    ERROR_LOG_FILE = "error.log"
    ACCESS_LOG_FILE = "access.log"

    # 日志轮转配置
    MAX_BYTES = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 10

    @classmethod
    def setup_logging(cls):
        """配置日志系统"""

        # 创建日志目录
        log_dir = Path(cls.LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)

        # 获取根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, cls.LOG_LEVEL))

        # 清除现有的处理器
        root_logger.handlers.clear()

        # 创建格式化器
        formatter = logging.Formatter(cls.LOG_FORMAT, datefmt=cls.LOG_DATE_FORMAT)

        # 1. 控制台处理器（彩色输出）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, cls.LOG_LEVEL))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # 2. 应用日志文件处理器（所有日志）
        app_log_path = log_dir / cls.APP_LOG_FILE
        app_handler = RotatingFileHandler(
            app_log_path,
            maxBytes=cls.MAX_BYTES,
            backupCount=cls.BACKUP_COUNT,
            encoding='utf-8'
        )
        app_handler.setLevel(getattr(logging, cls.LOG_LEVEL))
        app_handler.setFormatter(formatter)
        root_logger.addHandler(app_handler)

        # 3. 错误日志文件处理器（只记录ERROR及以上）
        error_log_path = log_dir / cls.ERROR_LOG_FILE
        error_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=cls.MAX_BYTES,
            backupCount=cls.BACKUP_COUNT,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)

        # 4. 访问日志文件处理器（记录HTTP请求）
        access_log_path = log_dir / cls.ACCESS_LOG_FILE
        access_handler = TimedRotatingFileHandler(
            access_log_path,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(formatter)

        # 配置uvicorn访问日志
        uvicorn_access_logger = logging.getLogger("uvicorn.access")
        uvicorn_access_logger.handlers.clear()
        uvicorn_access_logger.addHandler(access_handler)
        uvicorn_access_logger.setLevel(logging.INFO)
        uvicorn_access_logger.propagate = False

        # 配置uvicorn错误日志
        uvicorn_error_logger = logging.getLogger("uvicorn.error")
        uvicorn_error_logger.handlers.clear()
        uvicorn_error_logger.addHandler(app_handler)
        uvicorn_error_logger.addHandler(error_handler)
        uvicorn_error_logger.setLevel(getattr(logging, cls.LOG_LEVEL))
        uvicorn_error_logger.propagate = False

        # 配置第三方库日志级别
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("alibabacloud").setLevel(logging.INFO)

        # 记录配置信息
        logger = logging.getLogger(__name__)
        logger.info("=" * 80)
        logger.info("日志系统初始化完成")
        logger.info(f"日志级别: {cls.LOG_LEVEL}")
        logger.info(f"日志目录: {log_dir.absolute()}")
        logger.info(f"应用日志: {app_log_path}")
        logger.info(f"错误日志: {error_log_path}")
        logger.info(f"访问日志: {access_log_path}")
        logger.info("=" * 80)

        return root_logger


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return logging.getLogger(name)


# 便捷函数
def setup_uvicorn_logging():
    """配置uvicorn日志"""
    LogConfig.setup_logging()

    # 返回uvicorn配置
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": LogConfig.LOG_FORMAT,
                "datefmt": LogConfig.LOG_DATE_FORMAT,
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": LogConfig.LOG_LEVEL,
            },
            "uvicorn.error": {
                "level": LogConfig.LOG_LEVEL,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": "INFO",
            },
        },
    }
