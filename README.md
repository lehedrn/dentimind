# 口腔医院AI客服系统

基于阿里云百炼和CCC云联络中心构建的智能客服系统，支持文本客服、电话外呼、客户管理等功能。

## ✨ 功能特性

### 1. 文本客服 🤖
- 基于阿里云百炼智能体应用
- 支持多轮对话
- 自动提取口腔FAQ知识库答案
- 网页聊天界面：`http://localhost:8000/chat`

### 2. 电话外呼 📞
- 对接阿里云CCC云联络中心
- 自动外呼客户（人工接听）
- 通话记录查询
- 录音播放功能
- 管理界面：`http://localhost:8000/outbound`

**说明**：当前实现的是普通电话外呼功能，客户接听后由人工客服通话。未来可升级为AI语音对话。

### 3. 客户管理 👥
- 客户信息CRUD
- 通话记录关联
- 数据持久化（SQLite）
- 管理界面：`http://localhost:8000/customers`

### 4. 数据持久化 💾
- 客户信息存储
- 通话记录自动保存
- 对话会话记录
- 预约信息管理

### 5. Webhook回调 🔔
- CCC通话结果回调
- 自动更新通话记录
- 自动关联客户

## 🏗️ 技术架构

### 后端
- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **数据库**: SQLite（生产环境建议MySQL/PostgreSQL）
- **AI服务**: 阿里云百炼（qwen-plus）
- **电话服务**: 阿里云CCC（云联络中心）

### 前端
- **技术栈**: 原生HTML + CSS + JavaScript
- **界面**: 响应式设计，支持移动端

## 📋 前置要求

- Python 3.10+
- 阿里云账号（已开通百炼和CCC服务）
- CCC云联络中心体验版实例

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd dentimind
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下参数：

```bash
# 阿里云CCC配置
CCC_INSTANCE_ID=your-instance-id
ALIYUN_ACCESS_KEY_ID=your-access-key-id
ALIYUN_ACCESS_KEY_SECRET=your-access-key-secret
CCC_CALLER_NUMBER=your-caller-number
CCC_USER_ID=your-user-id
CCC_DEVICE_ID=device
CCC_REGION_ID=cn-shanghai

# 阿里云百炼配置
BAILIAN_APP_ID=your-app-id
DASHSCOPE_API_KEY=your-dashscope-api-key

# 服务配置
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=true

# 数据库配置
DATABASE_URL=sqlite:///./dental_ai.db
```

### 3. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r backend/requirements.txt
```

### 4. 初始化数据库

```bash
python scripts/init_db.py
```

### 5. 启动服务

```bash
# 方式1：使用服务管理脚本（推荐）
./service.sh start

# 方式2：直接启动
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. 访问应用

- **文本客服**: http://localhost:8000/chat
- **外呼管理**: http://localhost:8000/outbound
- **客户管理**: http://localhost:8000/customers
- **API文档**: http://localhost:8000/docs

## 📁 项目结构

```
dentimind/
├── backend/
│   ├── main.py                    # FastAPI主入口
│   ├── config.py                  # 配置管理
│   ├── routers/
│   │   ├── chat.py                # 文本客服API
│   │   ├── ccc.py                 # CCC电话API
│   │   ├── customers.py           # 客户管理API
│   │   └── webhook.py             # Webhook API
│   ├── services/
│   │   ├── bailian_chat.py        # 百炼对话服务
│   │   └── aliyun_ccc.py          # CCC电话服务
│   ├── models/
│   │   └── database.py            # 数据库模型
│   └── requirements.txt           # Python依赖
├── frontend/
│   ├── chat-widget.html           # 文本客服页面
│   ├── outbound.html              # 外呼管理页面
│   └── customers.html             # 客户管理页面
├── scripts/
│   ├── init_db.py                 # 数据库初始化脚本
│   ├── test_bailian.py            # 百炼测试脚本
│   ├── test_call_record_save.py   # 通话记录测试脚本
│   └── full_test.py               # 全流程测试脚本
├── docs/
│   ├── handoff-document.md        # 会话交接文档
│   ├── detailed-implementation-plan.md  # 详细实施计划
│   └── knowledge/
│       └── dental-faq-knowledge-base.md  # 口腔FAQ知识库
├── logs/                          # 日志目录
├── .env                           # 环境变量配置
├── service.sh                     # 服务管理脚本
└── README.md                      # 项目说明
```

## 🔧 API接口

### 文本客服

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat/new-session?message=xxx` | POST | 创建新会话 |
| `/api/chat/message` | POST | 发送消息 |

### CCC电话

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/ccc/outbound-call?callee_number=xxx` | POST | 发起外呼 |
| `/api/ccc/call-records?start_time=xxx&end_time=xxx` | GET | 查询通话记录 |
| `/api/ccc/recording/{contact_id}` | GET | 获取录音 |

### 客户管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/customers/` | GET | 获取客户列表 |
| `/api/customers/{id}` | GET | 获取客户详情 |
| `/api/customers/` | POST | 创建客户 |
| `/api/customers/{id}` | PUT | 更新客户 |
| `/api/customers/{id}` | DELETE | 删除客户 |
| `/api/customers/{id}/call-records` | GET | 获取客户通话记录 |

### Webhook

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/webhook/ccc/call-ended` | POST | CCC通话结束回调 |
| `/api/webhook/ccc/test` | POST | Webhook测试接口 |

## 🗄️ 数据库设计

系统使用SQLite数据库（`dental_ai.db`），包含以下表：

### customers（客户表）
- `id`: 主键（UUID）
- `name`: 客户姓名
- `phone`: 手机号（唯一索引）
- `notes`: 备注
- `created_at`: 创建时间
- `updated_at`: 更新时间

### call_records（通话记录表）
- `id`: 主键（UUID）
- `customer_id`: 客户ID（外键）
- `callee_number`: 被叫号码
- `call_id`: CCC通话ID
- `contact_id`: CCC联系人ID
- `status`: 通话状态
- `duration`: 通话时长（秒）
- `recording_url`: 录音URL
- `started_at`: 通话开始时间
- `ended_at`: 通话结束时间
- `created_at`: 创建时间
- `updated_at`: 更新时间

### appointments（预约表）
- `id`: 主键（UUID）
- `customer_id`: 客户ID（外键）
- `appointment_time`: 预约时间
- `service_type`: 服务类型
- `doctor_name`: 医生姓名
- `status`: 预约状态
- `notes`: 备注
- `created_at`: 创建时间
- `updated_at`: 更新时间

### chat_sessions（对话会话表）
- `id`: 主键（UUID）
- `customer_id`: 客户ID（外键，可选）
- `session_id`: 百炼会话ID
- `status`: 会话状态
- `created_at`: 创建时间
- `updated_at`: 更新时间

### chat_messages（对话消息表）
- `id`: 主键（UUID）
- `session_id`: 会话ID（外键）
- `role`: 角色（user/assistant）
- `content`: 消息内容
- `created_at`: 创建时间

## 🧪 测试

### 运行全流程测试

```bash
python scripts/full_test.py
```

测试内容包括：
1. 健康检查
2. 客户管理CRUD
3. 文本客服API
4. 通话记录自动保存
5. Webhook回调
6. 客户通话记录查询
7. 数据持久化

### 服务管理

```bash
# 查看服务状态
./service.sh status

# 启动服务
./service.sh start

# 停止服务
./service.sh stop

# 重启服务
./service.sh restart

# 查看实时日志
./service.sh logs
```

## 📝 使用示例

### 1. 文本客服

1. 打开浏览器访问：http://localhost:8000/chat
2. 输入问题，如："洗牙多少钱？"
3. AI会自动回复答案
4. 支持多轮对话

### 2. 电话外呼

1. 打开浏览器访问：http://localhost:8000/outbound
2. 输入客户手机号（需在CCC白名单中）
3. 点击"拨打"按钮
4. 系统自动发起外呼
5. **客户接听后，由人工客服通话**
6. 通话结束后，通话记录自动保存

**说明**：当前为普通电话外呼，非AI语音对话。

### 3. 客户管理

1. 打开浏览器访问：http://localhost:8000/customers
2. 点击"添加客户"按钮
3. 填写客户信息（姓名、手机号、备注）
4. 点击"保存"按钮
5. 可以查看、编辑、删除客户
6. 可以查看客户的通话记录

## ⚠️ 注意事项

1. **CCC白名单**: 外呼测试时，被叫号码必须在CCC白名单中
2. **百炼API响应**: 百炼API响应较慢（5-6秒），请耐心等待
3. **数据安全**: 生产环境请使用MySQL/PostgreSQL替代SQLite
4. **API Key安全**: 不要在代码中硬编码API Key，使用环境变量
5. **Webhook配置**: 如需接收CCC回调，需在CCC控制台配置Webhook地址

## 🔮 后续优化

- [ ] 用户认证和权限管理
- [ ] 通话录音文件存储
- [ ] 数据统计和报表
- [ ] 移动端APP支持
- [ ] 多渠道接入（微信、钉钉等）
- [ ] 智能质检和评分
- [ ] 客户画像和标签
- [ ] 预约管理和提醒

## 📄 许可证

MIT License

## 📞 联系方式

如有问题，请联系开发团队。

---

**祝您使用愉快！** 🚀
