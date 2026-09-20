# 口腔医院AI客服系统 — 完整实施路径

> 版本：v2.0  
> 日期：2026-09-14  
> 状态：待评审

---

## 一、方案概述

### 1.1 核心思路

使用阿里云两个产品作为基础设施，自己开发业务层：

| 阿里云产品 | 用途 | 你需要的操作 |
|---|---|---|
| **云联络中心（CCC）体验版** | 电话通道（呼入/呼出、ASR/TTS、通话管理） | 配置实例、白名单号码、获取API凭证 |
| **百炼平台** | 知识库（RAG）+ LLM对话能力 | 创建知识库、上传FAQ、创建智能体应用、获取API Key |

**你开发的系统**：
- Web管理后台（外呼任务、通话记录、客户管理）
- 文本客服（网页嵌入）
- 后端API服务（对接CCC和百炼）
- 数据库（客户、通话记录、预约）

### 1.2 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      你的系统（需要开发）                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              后端API服务（FastAPI/Python）              │   │
│  │  - 对接CCC OpenAPI（电话外呼、查询记录、获取录音）      │   │
│  │  - 对接百炼Application API（知识库+LLM对话）           │   │
│  │  - 业务逻辑（客户管理、预约管理、数据统计）             │   │
│  └──────────────────────────────────────────────────────┘   │
│           ↑                          ↑                       │
│           │                          │                       │
│  ┌────────┴─────────┐      ┌────────┴────────┐             │
│  │  Web管理后台      │      │  文本客服        │             │
│  │  - 外呼任务管理   │      │  - 网页聊天窗口  │             │
│  │  - 通话记录查询   │      │  - 嵌入官网      │             │
│  │  - 客户管理      │      │  - 在线咨询      │             │
│  │  - 数据统计      │      │                  │             │
│  └──────────────────┘      └─────────────────┘             │
│                                                              │
│                    数据库（MySQL/PostgreSQL）                  │
│              - customers（客户表）                            │
│              - call_records（通话记录表）                     │
│              - appointments（预约表）                         │
└─────────────────────────────────────────────────────────────┘
                      │                  │
                      │                  │
        ┌─────────────┘                  └─────────────┐
        │                                              │
        ▼                                              ▼
┌───────────────────────┐              ┌───────────────────────┐
│   阿里云CCC           │              │   阿里云百炼          │
│   (云联络中心)         │              │   (大模型服务平台)     │
│                        │              │                        │
│  - 电话线路（呼入/呼出）│              │  - 知识库（RAG）       │
│  - ASR语音识别          │              │  - LLM对话（通义千问） │
│  - TTS语音合成          │              │  - 智能体应用          │
│  - 坐席工作台           │              │  - Application API    │
│  - OpenAPI             │              │                        │
│  - 通话录音             │              │                        │
└───────────────────────┘              └───────────────────────┘
```

### 1.3 三个场景的实现

#### 场景1：文本客服（网页聊天）

```
用户在网页输入问题
    ↓
前端调用你的后端API → /api/chat/message
    ↓
后端调用百炼Application API
    ↓
百炼检索知识库 + LLM生成回复
    ↓
返回给前端显示
```

#### 场景2：AI外呼

```
在Web管理后台输入手机号，点击"拨打"
    ↓
前端调用你的后端API → /api/ccc/outbound-call
    ↓
后端调用CCC MakeCall API
    ↓
CCC拨打对方手机
    ↓
对方接听，CCC播放AI语音（CCC内置的AI或对接百炼）
    ↓
通话结束，CCC回调通知
    ↓
后端保存通话记录到数据库
```

**注意**：CCC体验版只能拨打白名单内的5个手机号。

#### 场景3：AI接听

```
客户拨打CCC分配的号码
    ↓
CCC接听，进入IVR流程
    ↓
转接到AI坐席（CCC内置AI或对接百炼）
    ↓
客户说话 → CCC ASR转文字 → 调用百炼API获取回复 → CCC TTS播放
    ↓
通话结束，保存记录
```

---

## 二、阿里云产品配置

### 2.1 云联络中心（CCC）体验版

#### 能力边界

| 项目 | 体验版限制 |
|---|---|
| 白名单号码 | 最多5个手机号 |
| 呼入/呼出 | 仅限白名单号码之间 |
| 测试号码 | 平台分配（长号码，需加分机号） |
| 通话量 | 有限（约50通） |
| API | 完整OpenAPI可用 |
| 坐席工作台 | 可用 |

#### 配置步骤

**Step 1：创建演示实例**

1. 登录 [CCC控制台](https://ccc.console.aliyun.com/)
2. 点击"新建演示项目"
3. 添加5个白名单手机号（用于测试呼入呼出）
4. 验证短信
5. 保存后获得实例ID

**Step 2：获取API凭证**

1. 登录 [阿里云RAM控制台](https://ram.console.aliyun.com/)
2. 创建子账号（或获取主账号AccessKey）
3. 给子账号授权CCC权限：`AliyunCCCFullAccess`
4. 获取 `AccessKey ID` 和 `AccessKey Secret`

**Step 3：熟悉坐席工作台**

1. 进入CCC控制台 → 演示实例 → 坐席工作台
2. 测试呼出：输入白名单手机号，点击拨打
3. 测试呼入：拨打平台提供的长号码，输入分机号
4. 查看通话记录和录音

**Step 4：记录关键信息**

```
CCC_INSTANCE_ID = "your-instance-id"
ALIYUN_ACCESS_KEY_ID = "your-access-key-id"
ALIYUN_ACCESS_KEY_SECRET = "your-access-key-secret"
```

#### CCC OpenAPI核心接口

| 接口 | 功能 | 用途 |
|---|---|---|
| `MakeCall` | 发起外呼 | Web后台点击拨打 |
| `ListCallDetailRecords` | 查询通话记录 | 展示通话历史 |
| `GetConversationDetail` | 获取通话详情 | 查看对话内容 |
| `GetMonoRecording` | 获取录音URL | 播放录音 |
| `ListPhoneNumbers` | 查询号码列表 | 获取分配的号码 |

---

### 2.2 百炼平台

#### 能力说明

| 功能 | 说明 |
|---|---|
| 知识库 | 支持文档（PDF/DOC/TXT）、网站（最多30页）、FAQ |
| LLM | 通义千问（qwen-plus/qwen-max等） |
| 智能体应用 | 可配置人设Prompt、关联知识库、插件 |
| Application API | 简单的对话接口，支持多轮对话 |
| 费用 | 按token计费，有免费额度 |

#### 配置步骤

**Step 1：创建知识库**

1. 登录 [百炼控制台](https://bailian.console.aliyun.com/)
2. 进入"知识库"模块
3. 点击"创建知识库"
4. 类型选择"文档搜索"
5. 上传口腔FAQ文档（`docs/knowledge/dental-faq-knowledge-base.md`）
6. 等待文档解析和索引构建完成（约5-10分钟）

**Step 2：创建智能体应用**

1. 进入"应用中心"
2. 点击"创建应用" → 选择"智能体应用"
3. 配置：
   - **应用名称**：口腔医院AI客服
   - **模型选择**：通义千问（qwen-plus，性价比高）
   - **关联知识库**：选择刚创建的口腔知识库
   - **人设Prompt**：

```markdown
你是XX口腔医院的AI客服助手，名叫小雅。

## 目标
热情、专业地回答患者的口腔健康问题，帮助患者了解服务项目和价格，引导患者预约就诊。

## 技能
1. 回答口腔健康常见问题（洗牙、补牙、种植牙、矫正、拔智齿等）
2. 介绍医院服务项目和价格
3. 帮助患者预约就诊（收集姓名、电话、项目、时间偏好）
4. 介绍门店位置和营业时间

## 约束
- 语气温和、耐心，像专业的医疗顾问
- 每次回复控制在50字以内（因为是语音通话）
- 不要给出具体医疗诊断，只给一般性建议
- 如果超出知识范围，说"这个问题建议您咨询我们的专业医生，我可以帮您预约"
- 涉及价格时，说明"具体价格需要医生检查后确定，我先给您一个参考范围"

## 开场白
"您好，这里是XX口腔医院，我是AI客服小雅，请问有什么可以帮您？"
```

4. 保存应用
5. 复制 **APP_ID**

**Step 3：获取API Key**

1. 进入"API Key管理"
2. 点击"创建API Key"
3. 保存 **DASHSCOPE_API_KEY**

**Step 4：测试对话**

1. 在应用详情页，点击"调试"
2. 输入问题："洗牙多少钱？"
3. 检查回复是否准确
4. 如果不准确，调整Prompt或补充知识库

**Step 5：记录关键信息**

```
BAILIAN_APP_ID = "your-app-id"
DASHSCOPE_API_KEY = "your-api-key"
```

#### 百炼Application API调用方式

```python
from dashscope import Application

response = Application.call(
    api_key="your-api-key",
    app_id="your-app-id",
    prompt="洗牙多少钱？",
    session_id="session-123"  # 多轮对话
)

print(response.output.text)  # AI回复
```

---

## 三、你的系统开发

### 3.1 技术栈

| 模块 | 技术选择 | 理由 |
|---|---|---|
| 后端 | Python + FastAPI | 快速开发，阿里云SDK支持好 |
| 前端 | HTML + JavaScript（或Vue/React） | 简单页面用原生，复杂页面用框架 |
| 数据库 | MySQL 或 PostgreSQL | 通用关系型数据库 |
| 部署 | 阿里云ECS + Docker | 与阿里云产品同网络，延迟低 |

### 3.2 项目结构

```
dental-ai-system/
├── backend/                          # 后端代码
│   ├── main.py                       # FastAPI入口
│   ├── config.py                     # 配置管理
│   ├── routers/                      # API路由
│   │   ├── __init__.py
│   │   ├── ccc.py                    # CCC电话相关API
│   │   ├── chat.py                   # 百炼对话API
│   │   └── customers.py              # 客户管理API
│   ├── services/                     # 业务逻辑
│   │   ├── __init__.py
│   │   ├── aliyun_ccc.py             # CCC SDK封装
│   │   └── bailian_chat.py           # 百炼SDK封装
│   ├── models/                       # 数据模型
│   │   ├── __init__.py
│   │   └── database.py               # SQLAlchemy模型
│   └── requirements.txt              # Python依赖
├── frontend/                         # 前端代码
│   ├── index.html                    # 首页/导航
│   ├── outbound.html                 # 外呼任务页
│   ├── call-records.html             # 通话记录页
│   ├── customers.html                # 客户管理页
│   └── chat-widget.html              # 文本客服页（可嵌入）
├── docs/                             # 文档
│   └── knowledge/
│       └── dental-faq-knowledge-base.md  # 口腔FAQ知识库
├── scripts/                          # 脚本
│   ├── init_db.py                    # 数据库初始化
│   └── test_api.py                   # API测试
├── .env                              # 环境变量（API Key等）
├── .gitignore
├── docker-compose.yml                # Docker编排
└── README.md                         # 项目说明
```

### 3.3 数据库设计

```sql
-- 客户表
CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notes TEXT,
    INDEX idx_phone (phone),
    INDEX idx_created (created_at)
);

-- 通话记录表
CREATE TABLE call_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    contact_id VARCHAR(100) UNIQUE,  -- CCC的contactId
    phone_number VARCHAR(20) NOT NULL,
    call_type ENUM('inbound', 'outbound') NOT NULL,
    status VARCHAR(20),  -- completed, no_answer, busy, failed
    duration INT DEFAULT 0,  -- 通话时长（秒）
    recording_url VARCHAR(500),
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    conversation_summary TEXT,  -- 对话摘要
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    INDEX idx_customer (customer_id),
    INDEX idx_contact (contact_id),
    INDEX idx_phone (phone_number),
    INDEX idx_started (started_at)
);

-- 预约表
CREATE TABLE appointments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    service_type VARCHAR(50),  -- 洗牙、补牙、种植牙等
    preferred_time TIMESTAMP,
    store_location VARCHAR(100),
    status ENUM('pending', 'confirmed', 'completed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    INDEX idx_customer (customer_id),
    INDEX idx_status (status),
    INDEX idx_time (preferred_time)
);

-- 文本对话记录表（可选）
CREATE TABLE chat_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(100) UNIQUE,  -- 百炼的session_id
    customer_id INT,
    source VARCHAR(20),  -- web, wechat, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    INDEX idx_session (session_id),
    INDEX idx_customer (customer_id)
);

CREATE TABLE chat_messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(100),
    role ENUM('user', 'assistant') NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id),
    INDEX idx_session (session_id),
    INDEX idx_created (created_at)
);
```

### 3.4 核心代码实现

#### 3.4.1 环境变量配置

```bash
# .env文件
# 阿里云CCC
CCC_INSTANCE_ID=your-ccc-instance-id
ALIYUN_ACCESS_KEY_ID=your-access-key-id
ALIYUN_ACCESS_KEY_SECRET=your-access-key-secret
CCC_CALLER_NUMBER=01012345678  # CCC分配的号码

# 阿里云百炼
BAILIAN_APP_ID=your-bailian-app-id
DASHSCOPE_API_KEY=your-dashscope-api-key

# 数据库
DATABASE_URL=mysql+pymysql://user:password@localhost/dental_ai
# 或
DATABASE_URL=postgresql://user:password@localhost/dental_ai
```

#### 3.4.2 百炼对话服务

```python
# backend/services/bailian_chat.py
import os
from http import HTTPStatus
from dashscope import Application

class BailianChatService:
    """
    封装百炼Application API调用
    """
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.app_id = os.getenv("BAILIAN_APP_ID")
    
    async def chat(self, session_id: str, prompt: str) -> dict:
        """
        调用百炼智能体应用API（多轮对话）
        
        Args:
            session_id: 会话ID，用于多轮对话
            prompt: 用户输入的问题
        
        Returns:
            {
                "text": "AI回复内容",
                "session_id": "会话ID",
                "finish_reason": "stop"
            }
        """
        response = Application.call(
            api_key=self.api_key,
            app_id=self.app_id,
            prompt=prompt,
            session_id=session_id
        )
        
        if response.status_code != HTTPStatus.OK:
            raise Exception(f"百炼API调用失败: {response.message}")
        
        return {
            "text": response.output.text,
            "session_id": response.output.session_id,
            "finish_reason": response.output.finish_reason,
        }
    
    async def chat_new_session(self, prompt: str) -> dict:
        """
        开始新会话
        """
        response = Application.call(
            api_key=self.api_key,
            app_id=self.app_id,
            prompt=prompt
        )
        
        if response.status_code != HTTPStatus.OK:
            raise Exception(f"百炼API调用失败: {response.message}")
        
        return {
            "text": response.output.text,
            "session_id": response.output.session_id,
            "finish_reason": response.output.finish_reason,
        }
```

#### 3.4.3 CCC电话服务

```python
# backend/services/aliyun_ccc.py
import os
from alibabacloud_ccc20200701.client import Client
from alibabacloud_ccc20200701 import models
from alibabacloud_tea_openapi.models import Config

class CCCService:
    """
    封装阿里云CCC OpenAPI调用
    """
    def __init__(self):
        config = Config(
            access_key_id=os.getenv("ALIYUN_ACCESS_KEY_ID"),
            access_key_secret=os.getenv("ALIYUN_ACCESS_KEY_SECRET"),
            endpoint="ccc.cn-shanghai.aliyuncs.com"  # 根据你的实例区域调整
        )
        self.client = Client(config)
        self.instance_id = os.getenv("CCC_INSTANCE_ID")
    
    async def make_call(self, callee_number: str) -> dict:
        """
        发起外呼
        
        Args:
            callee_number: 被叫号码（手机号）
        
        Returns:
            {
                "call_id": "通话ID",
                "status": "initiated"
            }
        """
        caller_number = os.getenv("CCC_CALLER_NUMBER")
        
        request = models.MakeCallRequest(
            instance_id=self.instance_id,
            caller_number=caller_number,
            callee_number=callee_number,
        )
        
        response = self.client.make_call(request)
        
        return {
            "call_id": response.body.call_id,
            "status": "initiated"
        }
    
    async def list_call_records(self, start_time: int, end_time: int, 
                                 page_number: int = 1, page_size: int = 50) -> list:
        """
        查询通话记录
        
        Args:
            start_time: 开始时间（Unix时间戳，毫秒）
            end_time: 结束时间（Unix时间戳，毫秒）
            page_number: 页码
            page_size: 每页数量
        
        Returns:
            通话记录列表
        """
        request = models.ListCallDetailRecordsRequest(
            instance_id=self.instance_id,
            start_time=start_time,
            end_time=end_time,
            page_number=page_number,
            page_size=page_size
        )
        
        response = self.client.list_call_detail_records(request)
        
        return response.body.data.list
    
    async def get_call_detail(self, contact_id: str) -> dict:
        """
        获取通话详情
        
        Args:
            contact_id: 通话ID
        
        Returns:
            通话详情
        """
        request = models.GetConversationDetailRequest(
            instance_id=self.instance_id,
            contact_id=contact_id
        )
        
        response = self.client.get_conversation_detail(request)
        
        return response.body.data
    
    async def get_recording_url(self, contact_id: str) -> str:
        """
        获取录音URL
        
        Args:
            contact_id: 通话ID
        
        Returns:
            录音文件URL
        """
        request = models.GetMonoRecordingRequest(
            instance_id=self.instance_id,
            contact_id=contact_id
        )
        
        response = self.client.get_mono_recording(request)
        
        return response.body.recording_url
```

#### 3.4.4 API路由

```python
# backend/routers/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.bailian_chat import BailianChatService

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    finish_reason: str

chat_service = BailianChatService()

@router.post("/message", response_model=ChatResponse)
async def send_message(req: ChatRequest):
    """
    发送消息给AI客服（多轮对话）
    """
    try:
        response = await chat_service.chat(req.session_id, req.message)
        return ChatResponse(
            session_id=response["session_id"],
            reply=response["text"],
            finish_reason=response["finish_reason"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/new-session")
async def new_chat_session(message: str):
    """
    开始新的对话会话
    """
    try:
        response = await chat_service.chat_new_session(message)
        return {
            "session_id": response["session_id"],
            "reply": response["text"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

```python
# backend/routers/ccc.py
from fastapi import APIRouter, HTTPException
from services.aliyun_ccc import CCCService

router = APIRouter(prefix="/api/ccc", tags=["CCC"])

ccc_service = CCCService()

@router.post("/outbound-call")
async def make_outbound_call(callee_number: str):
    """
    发起外呼
    """
    try:
        result = await ccc_service.make_call(callee_number)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/call-records")
async def list_call_records(start_time: int, end_time: int):
    """
    查询通话记录
    """
    try:
        records = await ccc_service.list_call_records(start_time, end_time)
        return {"records": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/call-detail/{contact_id}")
async def get_call_detail(contact_id: str):
    """
    获取通话详情
    """
    try:
        detail = await ccc_service.get_call_detail(contact_id)
        return detail
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recording/{contact_id}")
async def get_recording_url(contact_id: str):
    """
    获取录音URL
    """
    try:
        url = await ccc_service.get_recording_url(contact_id)
        return {"recording_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 3.4.5 FastAPI主入口

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import chat, ccc, customers

app = FastAPI(
    title="口腔医院AI客服系统",
    description="AI客服系统API - 对接阿里云CCC和百炼",
    version="1.0.0"
)

# CORS配置（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router)
app.include_router(ccc.router)
app.include_router(customers.router)

@app.get("/")
async def root():
    return {
        "message": "口腔医院AI客服系统API",
        "docs": "/docs"  # Swagger文档
    }

# 启动命令：uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3.5 前端页面

#### 3.5.1 文本客服页面

```html
<!-- frontend/chat-widget.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>在线咨询 - XX口腔医院</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        #chat-container { max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }
        #chat-header { background: #1890ff; color: white; padding: 15px; text-align: center; }
        #messages { height: 400px; overflow-y: auto; padding: 15px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 8px; max-width: 80%; }
        .message.user { background: #1890ff; color: white; margin-left: auto; }
        .message.bot { background: #f0f0f0; }
        #input-area { display: flex; padding: 15px; border-top: 1px solid #eee; }
        #user-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        #send-btn { margin-left: 10px; padding: 10px 20px; background: #1890ff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        #send-btn:hover { background: #40a9ff; }
    </style>
</head>
<body>
    <div id="chat-container">
        <div id="chat-header">
            <h3>XX口腔医院 - 在线咨询</h3>
        </div>
        <div id="messages"></div>
        <div id="input-area">
            <input type="text" id="user-input" placeholder="输入您的问题..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button id="send-btn" onclick="sendMessage()">发送</button>
        </div>
    </div>

    <script>
        let sessionId = 'session-' + Date.now();
        const API_BASE = 'http://localhost:8000';

        // 显示欢迎消息
        window.onload = function() {
            appendMessage('bot', '您好，这里是XX口腔医院，我是AI客服小雅，请问有什么可以帮您？');
        };

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            if (!message) return;

            input.value = '';
            appendMessage('user', message);

            try {
                const response = await fetch(`${API_BASE}/api/chat/message`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        message: message
                    })
                });

                const data = await response.json();
                appendMessage('bot', data.reply);
                sessionId = data.session_id;  // 更新session_id
            } catch (error) {
                appendMessage('bot', '抱歉，系统暂时出现问题，请稍后再试。');
                console.error(error);
            }
        }

        function appendMessage(sender, text) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = `message ${sender}`;
            div.textContent = text;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
    </script>
</body>
</html>
```

#### 3.5.2 外呼任务页面

```html
<!-- frontend/outbound.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>外呼任务 - 口腔医院AI客服</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h2 { margin-top: 0; }
        input[type="tel"] { padding: 10px; border: 1px solid #ddd; border-radius: 4px; width: 200px; }
        button { padding: 10px 20px; background: #1890ff; color: white; border: none; border-radius: 4px; cursor: pointer; margin-left: 10px; }
        button:hover { background: #40a9ff; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #fafafa; }
        .status-completed { color: #52c41a; }
        .status-no_answer { color: #faad14; }
        audio { height: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>发起外呼</h2>
            <input type="tel" id="phone-number" placeholder="输入客户手机号">
            <button onclick="makeCall()">拨打</button>
        </div>

        <div class="card">
            <h2>通话记录</h2>
            <table id="call-records">
                <thead>
                    <tr>
                        <th>号码</th>
                        <th>类型</th>
                        <th>状态</th>
                        <th>时长</th>
                        <th>时间</th>
                        <th>录音</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- 动态加载 -->
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const API_BASE = 'http://localhost:8000';

        async function makeCall() {
            const phoneInput = document.getElementById('phone-number');
            const phone = phoneInput.value.trim();
            
            if (!phone) {
                alert('请输入手机号');
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/api/ccc/outbound-call?callee_number=${phone}`, {
                    method: 'POST'
                });

                const result = await response.json();
                alert(`外呼已发起！\n通话ID: ${result.call_id}`);
                phoneInput.value = '';
                
                // 刷新通话记录
                loadCallRecords();
            } catch (error) {
                alert('外呼失败: ' + error.message);
                console.error(error);
            }
        }

        async function loadCallRecords() {
            const endTime = Date.now();
            const startTime = endTime - 7 * 24 * 60 * 60 * 1000;  // 最近7天

            try {
                const response = await fetch(`${API_BASE}/api/ccc/call-records?start_time=${startTime}&end_time=${endTime}`);
                const data = await response.json();
                
                const tbody = document.querySelector('#call-records tbody');
                tbody.innerHTML = '';
                
                data.records.forEach(record => {
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td>${record.callee_number || record.caller_number}</td>
                        <td>${record.call_type === 'outbound' ? '外呼' : '呼入'}</td>
                        <td class="status-${record.status}">${record.status}</td>
                        <td>${record.duration || 0}秒</td>
                        <td>${new Date(record.start_time).toLocaleString()}</td>
                        <td>${record.recording_url ? `<audio controls src="${record.recording_url}"></audio>` : '-'}</td>
                    `;
                });
            } catch (error) {
                console.error('加载通话记录失败:', error);
            }
        }

        // 页面加载时获取通话记录
        window.onload = loadCallRecords;
    </script>
</body>
</html>
```

---

## 四、实施计划

### 4.1 时间线（2周）

#### Week 1：基础搭建

| Day | 任务 | 交付物 |
|---|---|---|
| 1 | 阿里云配置：CCC体验版 + 百炼知识库 + 智能体应用 | 拿到所有API凭证 |
| 2 | 本地开发环境搭建：Python + FastAPI + 依赖安装 | 项目骨架运行 |
| 3-4 | 实现百炼对话API对接，测试文本客服 | `/api/chat/message` 可用 |
| 5-6 | 实现CCC API对接：外呼、查询记录、获取录音 | `/api/ccc/*` 可用 |
| 7 | 前端文本客服页面 + 外呼管理页面 | 两个页面可用 |

#### Week 2：完善功能

| Day | 任务 | 交付物 |
|---|---|---|
| 8-9 | 数据库设计和客户管理功能 | 客户数据可管理 |
| 10-11 | Webhook接收（通话结果回调）、数据同步 | 通话记录自动保存 |
| 12-13 | 全流程联调、优化UI/UX | 三个场景全部跑通 |
| 14 | 演示准备、内部演练 | 可以面对客户演示 |

### 4.2 里程碑

| 里程碑 | 时间 | 验收标准 |
|---|---|---|
| M1: 文本客服可用 | Day 7 | 打开网页，输入问题，AI准确回答 |
| M2: 外呼功能可用 | Day 11 | 点击拨打，白名单手机响铃，AI对话 |
| M3: 完整系统可用 | Day 14 | 三个场景全部演示通过 |

---

## 五、成本估算

### 5.1 阿里云费用

| 产品 | 费用 | 说明 |
|---|---|---|
| CCC体验版 | 免费 | 限50通，5个白名单号码 |
| 百炼平台 | 按token计费 | 有免费额度，演示阶段约10-50元/月 |
| ECS服务器（2核4G） | 约100元/月 | 运行你的后端服务 |
| 数据库（RDS基础版） | 约50元/月 | 或用服务器本地数据库 |
| **总计** | **约150-200元/月** | 演示阶段 |

### 5.2 生产阶段（合同签署后）

| 产品 | 费用 | 说明 |
|---|---|---|
| CCC正式版 | 199元/月/坐席 + 通话费 | 通话费约0.08-0.15元/分钟 |
| 百炼平台 | 按实际用量 | 根据对话量估算 |
| 服务器 | 300-600元/月 | 根据负载升级 |
| **总计** | **约2000-5000元/月** | 根据业务量 |

---

## 六、风险与应对

| 风险 | 影响 | 应对方案 |
|---|---|---|
| CCC体验版号码限制 | 只能测试5个白名单号码 | 演示时用自己的手机，或申请正式版 |
| 百炼知识库检索不准 | AI回答不准确 | 优化Prompt，补充FAQ，调整知识库分段 |
| CCC对接复杂 | 开发周期延长 | 先用CCC内置AI，后续再对接百炼 |
| 服务器性能不足 | 系统卡顿 | 升级配置，或分离部署 |

---

## 七、后续扩展

合同签署后，可以扩展的功能：

1. **企业微信集成**：将AI客服接入企业微信，自动回复客户咨询
2. **私域SOP**：自动发送预约提醒、术后回访等
3. **多门店管理**：每个门店独立的知识库和统计数据
4. **CRM集成**：对接医院的客户管理系统
5. **数据分析**：通话记录分析、客户画像、转化率统计

---

## 八、待确认事项

在开始实施前，需要确认：

1. **阿里云账号**：是否已开通CCC体验版和百炼平台？
2. **白名单号码**：CCC体验版的5个白名单手机号是什么？
3. **服务器**：是否已购买阿里云ECS？配置如何？
4. **域名**：是否需要配置域名和HTTPS？（用于生产环境）
5. **数据库**：使用MySQL还是PostgreSQL？本地还是RDS？

---

## 附录：关键文档链接

### 阿里云CCC

- [产品主页](https://www.aliyun.com/product/ccc)
- [快速入门](https://help.aliyun.com/zh/ccs/cccai/getting-started/quickly-create-a-cloud-contact-center-voice-business-experience-edition)
- [API概览](https://help.aliyun.com/zh/ccs/cccai/developer-reference/api-ccc-2020-07-01-overview)
- [OpenAPI门户](https://api.aliyun.com/product/CCC)

### 阿里云百炼

- [产品主页](https://www.aliyun.com/product/bailian)
- [知识库文档](https://help.aliyun.com/zh/model-studio/rag-knowledge-base)
- [调用智能体应用](https://help.aliyun.com/zh/model-studio/call-single-agent-application)
- [获取API Key](https://help.aliyun.com/zh/model-studio/get-api-key)

### SDK文档

- [CCC Python SDK](https://help.aliyun.com/zh/ccs/cccai/developer-reference/api-ccc-2020-07-01-overview)
- [百炼DashScope SDK](https://github.com/dashscope/dashscope-sdk-python)

---

**文档版本**：v2.0  
**最后更新**：2026-09-14  
**状态**：待评审
