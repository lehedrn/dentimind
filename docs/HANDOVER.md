# 项目交接文档

> **项目**：口腔医院AI客服系统（dentimind）
> **版本**：v0.0.2（开发中）
> **交接时间**：2026-10-26
> **当前分支**：`develop/v0.0.2`（主分支 `main`）
> **远程仓库**：`https://github.com/lehedrn/dentimind.git`

本文档面向**接手开发的同事**，目标是让你从零开始把系统跑起来，并清楚目前做到哪了、还有什么没做、有哪些坑。

---

## 一、项目是什么

为口腔医院做的一套客服系统，对接两个阿里云服务：

- **阿里云百炼**（LLM 智能体）：驱动网页端的**文字客服**，24 小时自动回答患者咨询（洗牙多少钱、矫正方案、挂号流程等）。
- **阿里云 CCC**（云联络中心）：驱动**电话外呼**（系统拨号 → 客户/坐席接听）和**电话呼入**（客户拨打医院 DID 号码 → 坐席用软电话接听）。

⚠️ **重要澄清**：当前**所有电话功能都是"人工通话"**——AI 只处理文字，不参与语音。AI 电话（ASR+TTS+对话）是未来的升级方向，代码里没有任何实现。

---

## 二、技术栈一览

| 层 | 技术 | 说明 |
|---|---|---|
| 后端 | Python 3.10+ / FastAPI 0.104 | 单进程，`backend/main.py` 入口 |
| ORM | SQLAlchemy 2.0 | 声明式，5 张表 |
| 数据库 | SQLite（`dental_ai.db`） | 开发/演示用；生产建议换 MySQL/PostgreSQL |
| AI | 阿里云百炼 `dashscope` SDK 1.14 | 智能体应用（模型由 `BAILIAN_APP_ID` 对应的应用配置决定，代码层不指定） |
| 电话 | 阿里云 CCC SDK `alibabacloud-ccc20200701` | 外呼/呼入/录音/坐席管理 |
| 前端 | **原生 HTML + CSS + JS**（无框架、无构建） | 直接改 HTML 即时生效 |
| 软电话 | 阿里云 CCC `WorkbenchSdk`（JS SDK，CDN 引入） | 前端 WebRTC 接听呼入 |
| 进程管理 | `service.sh` + uvicorn | 支持 HTTPS 自动检测 |

---

## 三、从零把系统跑起来

### 3.1 前置条件

1. **Python 3.10+**
2. **阿里云账号**，已开通：
   - 百炼（DashScope）：拿到 `DASHSCOPE_API_KEY` 和 `BAILIAN_APP_ID`
   - CCC 云联络中心：拿到 `CCC_INSTANCE_ID`、AccessKey、外呼号码、坐席账号等
3. **CCC 白名单**：外呼测试时，被叫号码必须在 CCC 体验版白名单里
4. **HTTPS 已默认启用**：`.env` 里配了 `SSL_CERT_FILE=certs/localhost+1.pem` 和 `SSL_KEY_FILE=certs/localhost+1-key.pem`，`service.sh` 会自动让 uvicorn 走 HTTPS。`certs/` 目录里已有 mkcert 生成的 `localhost` 自签证书，本地开发直接用。如要换正式证书，替换这两个文件路径即可；如要关闭 HTTPS（不推荐），清空 `.env` 里这两个变量。

### 3.2 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/lehedrn/dentimind.git
cd dentimind

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入真实的阿里云凭证（见下节"关键配置"）

# 3. 创建虚拟环境 + 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 4. 初始化数据库（首次启动会自动建表，手动跑一次也无妨）
python scripts/init_db.py

# 5. 启动
./service.sh start     # 后台启动，推荐
# 或：uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload   # 开发调试
```

### 3.3 验证

- 健康检查：`curl -k https://localhost:8000/health`
- API 文档（Swagger）：https://localhost:8000/docs
- 文本客服页面：https://localhost:8000/chat
- 外呼管理：https://localhost:8000/outbound
- 客户管理：https://localhost:8000/customers
- CCC 工作台（软电话）：https://localhost:8000/ccc-workbench

> 浏览器打开 https://localhost 时，自签证书会触发告警，点"高级 → 继续访问"即可。curl 验证时要加 `-k` 跳过证书校验。

### 3.4 常用命令

| 用途 | 命令 |
|---|---|
| 启动服务 | `./service.sh start` |
| 停止服务 | `./service.sh stop` |
| 重启 | `./service.sh restart` |
| 状态 | `./service.sh status` |
| 实时日志 | `./service.sh logs` |
| 全流程测试 | `python scripts/full_test.py`（需服务运行中） |
| 单独测百炼 | `python scripts/test_bailian.py` |
| 单独测通话记录 | `python scripts/test_call_record_save.py` |

注意：项目**没有 pytest**，所有测试都是调用运行中服务的集成脚本。

---

## 四、关键配置（.env）

完整示例见 `.env.example`，关键项：

| 键 | 用途 | 在哪拿 |
|---|---|---|
| `CCC_INSTANCE_ID` | CCC 实例 ID | CCC 控制台 → 实例管理 |
| `ALIYUN_ACCESS_KEY_ID` / `SECRET` | 阿里云 AK/SK | RAM 控制台 |
| `CCC_CALLER_NUMBER` | CCC 分配的 DID 号码（外呼显示 + 呼入识别） | CCC 控制台 → 号码管理 |
| `CCC_USER_ID` | 坐席账号（形如 `用户名@实例ID`） | CCC 控制台 → 坐席管理 |
| `CCC_REGION_ID` | CCC 区域，默认 `cn-shanghai` | 看实例区域 |
| `BAILIAN_APP_ID` | 百炼智能体应用 ID | 百炼控制台 |
| `DASHSCOPE_API_KEY` | 百炼 API Key | 百炼控制台 |
| `DATABASE_URL` | 数据库 URL | 默认 `sqlite:///./dental_ai.db` |
| `SSL_CERT_FILE` / `SSL_KEY_FILE` | HTTPS 证书（当前已配置，默认启用） | `certs/` 目录有 mkcert 自签证书 |
| `CCC_WEBHOOK_URL` | CCC 通话回调地址（代码里读了但未使用，**需要直接在 CCC 控制台手动配置**） | 需公网可达，本地用 ngrok |
| `WHITE_LIST_PHONE` | 通过 `/api/config` 暴露给前端，但**当前前端未消费**，留着备用 | 配合 CCC 白名单 |

⚠️ `.env` 已在 `.gitignore` 中，**不要提交**。

---

## 五、代码架构速览

```
dentimind/
├── backend/
│   ├── main.py              # FastAPI 入口：挂 router、静态文件、HTTPS 配置
│   ├── config.py            # 从 .env 读所有配置，集中访问
│   ├── logging_config.py    # 日志系统（多文件输出）
│   ├── routers/             # API 路由（HTTP 入口）
│   │   ├── chat.py          # /api/chat/*         文字客服
│   │   ├── ccc.py           # /api/ccc/*          外呼 API
│   │   ├── ccc_proxy.py     # CCC OpenAPI 通用代理（前端 WorkbenchSdk 用）
│   │   ├── softphone.py     # /api/softphone/*    软电话事件处理
│   │   ├── customers.py     # /api/customers/*    客户 CRUD
│   │   └── webhook.py       # /api/webhook/*      CCC 通话回调
│   ├── services/            # 业务逻辑
│   │   ├── bailian_chat.py  # 百炼 LLM 调用
│   │   └── aliyun_ccc.py    # CCC SDK 封装
│   └── models/database.py   # SQLAlchemy 模型（5 张表）
├── frontend/                # 纯 HTML，无构建
│   ├── chat-widget.html     # /chat
│   ├── outbound.html        # /outbound
│   ├── customers.html       # /customers
│   ├── ccc-workbench.html   # /ccc-workbench（软电话工作台）
│   ├── softphone.html       # /softphone
│   └── ...
├── scripts/                 # 数据库初始化、测试脚本
├── docs/                    # 各类文档（含本交接文档）
├── certs/                   # 自签 HTTPS 证书
├── logs/                    # 服务日志
├── service.sh               # 服务管理脚本
└── CLAUDE.md                # Claude Code 项目指引
```

**调用链**：前端 → `routers/*` → `services/*` → 阿里云百炼/CCC 或 SQLite。

**数据库 5 张表**：`Customer`、`CallRecord`、`Appointment`、`ChatSession`、`ChatMessage`。主键全部 UUID。`CallRecord` 通过 `customer_id` 外键关联 `Customer`，并通过 `direction` 字段（`inbound`/`outbound`）区分呼入/呼出。

---

## 六、功能状态（最新）

### ✅ 已完成、可用

| 模块 | 状态 | 入口 | 备注 |
|---|---|---|---|
| 文字客服 | ✅ 已测试 | `/chat` | 百炼多轮对话，响应较慢（5-6 秒），正常 |
| 电话外呼 | ✅ 已测试 | `/outbound` | 系统拨号 → 人工接听；自动签到、通话记录保存、录音 |
| 客户管理 | ✅ 已测试 | `/customers` | CRUD + 通话记录关联 + Toast 提示 |
| 呼入 Webhook | ✅ 代码完成并自测 | `/api/webhook/ccc/call-ended` | 智能识别方向、自动关联客户 |
| CCC 通用代理 | ✅ 已实现 | `/api/ccc-proxy` | 动态转发前端 WorkbenchSdk 请求到 CCC OpenAPI |
| 软电话事件处理 | ✅ 已实现 | `/api/softphone/*` | 接收前端 SDK 推送的通话事件、落库 |
| 日志系统 | ✅ | `backend/logs/*` | 应用日志 / 错误日志 / 访问日志 分离 |

### ⚠️ 代码完成、但**未在生产 CCC 控制台配置过**

| 模块 | 风险点 |
|---|---|
| **呼入功能（真实电话呼入）** | 代码写完、本地 Webhook 自测通过，但**没有真实电话呼入过**。需要：① CCC 控制台配置呼入号码路由 ② 配置 Webhook 回调地址（要公网可达）③ 真实呼入测试 |
| **CCC 工作台（软电话）** | 前端 `ccc-workbench.html` 用了 `WorkbenchSdk`，需要 CCC 控制台正确配置坐席、技能组、呼入路由才能实际接听 |

### ❌ 完全未实现（属于后续升级）

- **AI 电话外呼**（AI 自动拨号 + 与客户语音对话）
- **AI 电话接听**（AI 自动接呼入 + 语音对话 + 智能转人工）

这两项需要 ASR + TTS + 实时对话栈，当前代码里**一行都没有**，别误以为藏在哪里。

---

## 七、已知的坑

下面这些问题**已经修过**，但你改动相关代码时**要小心不要再踩**：

1. **CCC SDK 属性名是 PascalCase，不是 snake_case**
   CCC SDK 返回的 `Data.CallContext.JobId` 用 `.call_context.job_id` 取不到。`backend/services/aliyun_ccc.py` 里做了兼容（PascalCase + snake_case + 正则回退）。**改这段代码时请仔细看注释**。

2. **呼入/呼出客户匹配逻辑不一样**
   - 呼出：客户 = `callee_number`
   - 呼入：客户 = `caller_number`
   - `webhook.py` 里有智能方向检测逻辑，**不要简单按 `callee_number` 找客户**。

3. **`CallRecord.call_id` 曾经存了整个 CCC 响应体**
   之前 bug 把整个 JSON 字符串塞进 `call_id`，已修。`ccc.py` 外呼路由有防御：长度 >100 或以 `{` 开头会拒绝存储。**不要回退这个校验**。

4. **数据库自动迁移**
   `database.py` 里有一段启动时检查并添加 `caller_number` / `direction` 字段的代码。新增字段时记得照这个模式写迁移，否则老数据库起不来。

5. **百炼 API 响应慢**
   单次调用 5-6 秒，是 API 本身的限制，不是代码问题。前端已做 loading 状态，不要为了"优化"去改超时设置。

6. **CCC 体验版白名单**
   外呼被叫必须在 CCC 控制台白名单里，否则会被拒。`WHITE_LIST_PHONE` 环境变量是给前端做过滤提示用的，真正的白名单在 CCC 控制台配。

7. **Webhook 需要公网可达**
   本地开发用 `ngrok http https://localhost:8000`（注意是 https），拿到公网 URL 后去 CCC 控制台配置。**`CCC_WEBHOOK_URL` 这个 `.env` 变量代码里读了但没消费**，你最终还是要去 CCC 控制台手动填 Webhook URL，不要以为配了环境变量就完事。

---

## 八、下一步建议做的事

按优先级，从**最能帮到你**到**可以放着不管**：

1. **跑通一次真实呼入**
   在 CCC 控制台配好呼入号码路由 + Webhook 回调 → 用真实手机拨打 DID → 看 `backend/logs/app.log` 和数据库 `call_records` 表有没有正确记录 → 用软电话接听。这一步通了，呼入模块才算真的完成。

2. **跑通一次完整外呼**
   配好 CCC 控制台 Webhook → 在外呼页面发起外呼 → 看 Webhook 是否收到回调更新通话记录。

3. **准备演示数据**
   数据库现在是空的。建议加 3-5 个真实客户 + 几条通话记录，演示时好看。`scripts/` 里的脚本可参考。

4. **换数据库（如要上生产）**
   SQLite 单机用可以，多用户并发、上生产必须换 MySQL 或 PostgreSQL。改 `DATABASE_URL` + 安装对应驱动即可，ORM 层不用动。

5. **考虑认证**
   当前所有 API 都没鉴权，任何人能访问 `/customers` 删客户。上生产前必须加。

---

## 九、账号 / 控制台入口

- **阿里云 CCC 控制台**：实例管理、坐席管理、号码管理、Webhook 配置、白名单
- **阿里云百炼控制台**：智能体应用管理、API Key
- **阿里云 RAM 控制台**：AccessKey（建议用子账号，不要用主账号 AK）
- **GitHub 仓库**：`https://github.com/lehedrn/dentimind`，当前只有 `lehedrn` 一个协作者

⚠️ 真实的 AK/SK、`DASHSCOPE_API_KEY` 等都在接手同事自己的 `.env` 里，**不要通过任何聊天工具明文传输**，让对接人直接在阿里云控制台重置并自己保存。

---

## 十、日常运维

**看日志**
```bash
./service.sh logs                       # 实时看服务日志
tail -f backend/logs/app.log            # 应用日志（含 HTTP 请求、业务逻辑）
tail -f backend/logs/error.log          # 错误日志（只看报错）
tail -f logs/server.log                 # uvicorn 启停日志
```

**重启服务**（改完代码后）
```bash
./service.sh restart
```

**数据库备份**
SQLite 直接拷文件即可：
```bash
cp dental_ai.db dental_ai.db.bak-$(date +%F)
```

**健康检查**
```bash
curl -k https://localhost:8000/health
```

---

## 十一、相关文档索引

仓库里文档很多，容易迷路。按用途整理：

| 想看什么 | 读哪个 |
|---|---|
| 整体介绍 + 快速开始 | `README.md` |
| Claude Code 项目指引 | `CLAUDE.md` |
| 本次交接（本文） | `docs/HANDOVER.md` |
| 系统能力 / 功能边界 | `docs/system-capability-status.md` |
| 呼入模块修复细节 | `docs/inbound-fix-report-2026-09-16.md` |
| 呼入模块重构方案 | `docs/呼入模块重构方案.md` |
| 坐席状态管理 | `docs/agent-status-management.md` |
| 日志系统说明 | `docs/logging-guide.md` |
| 常见问题 | `docs/faq.md` |
| 演示流程 | `docs/demo-guide.md` |
| 手动测试指南 | `docs/manual-test-guide.md` |
| 百炼 Prompt 配置 | `docs/config/bailian-prompt-config.md` |
| 口腔 FAQ 知识库 | `docs/knowledge/dental-faq-knowledge-base.md` |
| 前端 SDK 接入参考 | `docs/references/前端sdk文档接入.md` |

`docs/` 里还有一些**历史过程文档**（`handoff-2026-09-15-evening.md`、`session-handoff.md`、`tomorrow-tasks.md`、`detailed-implementation-plan.md` 等），是过去每天的工作记录，**已经过时**，仅供参考脉络，**不要按里面描述的"当前状态"来理解项目**。

---

## 十二、给接手同事的几点建议

1. **先把系统完整跑一遍**：按第三节把服务起起来，把 `/chat`、`/outbound`、`/customers`、`/ccc-workbench` 四个页面都点一遍，有个感性认识。

2. **再看一遍 API 文档**：访问 https://localhost:8000/docs，所有接口都在 Swagger 里，比看代码快。

3. **读 `backend/main.py`**：这是整个后端的骨架，看完就知道所有 router 怎么挂的、静态文件怎么服务的。

4. **别被 `docs/` 里的历史文档吓到**：很多是过去某个会话的产物，重复且互相覆盖。遇到具体问题时再查，不要试图通读。

5. **改代码前先跑一遍 `full_test.py`**：作为基线，确保改动没破坏现有功能。

6. **阿里云控制台是关键**：CCC 的很多配置（白名单、Webhook、呼入路由、坐席签到）都必须在控制台操作，代码只是 API 调用。遇到问题**第一反应是去控制台看配置**，第二反应才是看代码。

7. **有问题先看日志**：`backend/logs/app.log` 里有详细的请求/响应日志，90% 的问题看日志就能定位。

---

**祝接手顺利。** 🎯
