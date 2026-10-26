# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

口腔医院AI客服系统 — 基于阿里云百炼（LLM）和阿里云CCC云联络中心构建的智能客服系统。提供三大能力：文本客服（对接百炼智能体）、电话外呼（CCC，当前为人工接听，非AI语音）、客户管理（CRUD + 通话记录关联）。

## Commands

### 服务启动 / 管理（使用 `service.sh`）

```bash
./service.sh start        # 启动服务（后台）
./service.sh stop         # 停止
./service.sh restart      # 重启
./service.sh status       # 查看状态
./service.sh logs         # tail 实时日志
```

`service.sh` 读取 `.env` 中的 `SSL_CERT_FILE` / `SSL_KEY_FILE`，若配置且文件存在则自动启用 HTTPS；否则走 HTTP。

### 直接启动（开发调试）

```bash
source venv/bin/activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 测试

```bash
source venv/bin/activate
python scripts/full_test.py        # 全流程测试（健康检查 / 客户CRUD / 聊天 / 通话记录 / Webhook）
python scripts/test_bailian.py     # 单独测试百炼对话
python scripts/test_call_record_save.py   # 通话记录保存
python scripts/init_db.py          # 初始化数据库
```

没有单元测试框架（无 pytest），测试都是集成脚本，直接调用运行中的服务（默认 `http://localhost:8000`）。

### 依赖

```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

依赖版本锁在 `requirements.txt`，无 lockfile。主要依赖：FastAPI 0.104、SQLAlchemy 2.0、dashscope 1.14（百炼）、alibabacloud-ccc20200701（CCC SDK）。

## Architecture

### 后端结构（FastAPI，单进程）

```
backend/
├── main.py            # FastAPI app 入口，挂载所有 router + 静态文件
├── config.py          # Config 类：从 .env 读取所有配置，模块集中访问
├── logging_config.py  # 日志配置
├── routers/           # API 路由（业务入口）
│   ├── chat.py        # /api/chat/*   文本客服
│   ├── ccc.py         # /api/ccc/*    CCC 电话外呼 / 录音 / 通话记录
│   ├── ccc_proxy.py   # CCC 代理接口（无 prefix）
│   ├── softphone.py   # /api/softphone/*  软电话
│   ├── customers.py   # /api/customers/*  客户 CRUD
│   └── webhook.py     # /api/webhook/*    CCC 回调接收
├── services/          # 业务逻辑（被 routers 调用）
│   ├── bailian_chat.py    # 封装百炼 LLM 调用（多轮会话）
│   └── aliyun_ccc.py      # 封装阿里云 CCC SDK
└── models/
    └── database.py    # SQLAlchemy 模型 + engine + init_db()
```

**调用链**：`routers/*` → `services/*` → 外部 API（百炼 / CCC）/ SQLite。Routers 负责 HTTP 协议和参数校验，Services 负责业务逻辑和第三方对接，Models 负责数据持久化。

### 前端结构（原生 HTML，无构建）

```
frontend/
├── chat-widget.html       # 文本客服页面 → /chat
├── outbound.html          # 外呼管理 → /outbound
├── customers.html         # 客户管理 → /customers
├── softphone.html / softphone-test.html   # 软电话
├── ccc-workbench.html     # CCC 工作台
└── test-direct-api.html   # API 调试
```

`main.py` 通过 `app.mount("/static", StaticFiles(directory=frontend_dir))` 挂载静态文件，并直接 `FileResponse` 返回根路径 HTML（`/chat`、`/outbound`、`/customers`）。**前端无构建步骤、无框架、纯原生 JS + HTML**，直接修改即时生效。

### 数据库

SQLite 文件 `dental_ai.db`（项目根目录）。5 张表：`Customer`、`CallRecord`、`Appointment`、`ChatSession`、`ChatMessage`。

- ORM：SQLAlchemy 2.0，声明式（`declarative_base()`）。
- 初始化：`init_db()` 在 `main.py` 启动时调用，`scripts/init_db.py` 手动重建。
- 外键关系：`CallRecord`、`Appointment`、`ChatSession` 都通过 `customer_id` 外键关联 `Customer`。
- 主键全部用 UUID 字符串。

### 外部服务对接

- **阿里云百炼**（`services/bailian_chat.py`）：通过 `dashscope` SDK 调用智能体应用，支持多轮会话（session_id 透传）。响应较慢（5-6 秒）。
- **阿里云 CCC**（`services/aliyun_ccc.py`）：使用 `alibabacloud-ccc20200701` SDK，提供外呼、查询通话记录、获取录音 URL 等。被叫号码必须在 CCC 白名单中。
- **Webhook**（`routers/webhook.py`）：接收 CCC 通话结束回调，自动更新 `CallRecord` 并关联客户。

### 配置加载

`backend/config.py` 通过 `python-dotenv` 在模块加载时 `load_dotenv()`，所有配置从 `.env` 读取。复制 `.env.example` 为 `.env` 后填入阿里云凭证。关键配置：`CCC_INSTANCE_ID`、`ALIYUN_ACCESS_KEY_ID/SECRET`、`CCC_CALLER_NUMBER`、`BAILIAN_APP_ID`、`DASHSCOPE_API_KEY`。

## 注意事项

- `.env` 包含阿里云 AccessKey，已被 `.gitignore`，**不要提交**。
- `venv/` 是本地虚拟环境，不提交；`dental_ai.db` 也不提交。
- 当前分支 `develop/v0.0.2`，主分支 `main`。
- 仓库无 CodeGraph 索引（无 `.codegraph/` 目录），需要时用 `codegraph explore` 或直接 Read/Grep。
