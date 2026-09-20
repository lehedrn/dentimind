# 口腔医院AI客服系统 — 详细实施计划（1周）

> 版本：v4.0  
> 日期：2026-09-15  
> 实施周期：7天  
> 开发者：Claude Code

---

## 📋 前置准备（Day 0 — 已完成 ✅）

### 你（用户）的任务

- [x] **开通阿里云产品**
  - [x] 登录阿里云，开通 CCC云联络中心体验版
  - [x] 登录阿里云，开通百炼平台

- [x] **配置CCC体验版**
  - [x] 创建演示实例
  - [x] 添加5个白名单手机号（用于测试呼入呼出）
  - [x] 记录 `CCC_INSTANCE_ID`

- [x] **配置百炼平台**
  - [x] 创建知识库（类型：文档搜索）
  - [x] 上传口腔FAQ文档（我提供内容）
  - [x] 创建智能体应用，关联知识库
  - [x] 配置AI人设Prompt（我提供模板）
  - [x] 记录 `BAILIAN_APP_ID`

- [x] **获取API凭证**
  - [x] RAM控制台创建子账号
  - [x] 授权 `AliyunCCCFullAccess` 权限
  - [x] 获取 `ACCESS_KEY_ID` 和 `ACCESS_KEY_SECRET`
  - [x] 百炼API Key管理，创建 `DASHSCOPE_API_KEY`

- [x] **准备服务器环境**
  - [x] 确认本地Python版本（需要3.10+）
  - [x] 确认本地MySQL/PostgreSQL已安装（或用SQLite临时替代）

- [x] **信息确认**
  - [x] 告诉我数据库选择（MySQL/PostgreSQL/SQLite）→ SQLite（临时）
  - [x] 告诉我部署方式（本地/ECS）→ 本地
  - [x] 提供医院名称（用于AI客服开场白）→ 口腔医院

### 我的任务（已完成 ✅）

- [x] 生成口腔FAQ知识库内容（Markdown格式）
- [x] 准备百炼智能体Prompt模板
- [x] 准备环境变量配置模板（.env.example）

---

## ✅ Day 1：基础搭建 + 百炼对话联调（已完成）

### 已完成

- [x] **项目初始化**
  - [x] 创建项目目录 `dental-ai-system/`
  - [x] 创建后端目录 `backend/`
  - [x] 创建前端目录 `frontend/`
  - [x] 创建文档目录 `docs/knowledge/`
  - [x] 创建脚本目录 `scripts/`
  - [x] 编写 `requirements.txt`

- [x] **百炼对话服务**
  - [x] 创建 `backend/services/bailian_chat.py`
  - [x] 实现 `BailianChatService` 类
  - [x] 实现 `chat()` 方法（多轮对话）
  - [x] 实现 `chat_new_session()` 方法（新会话）
  - [x] 添加错误处理和日志记录

- [x] **FastAPI框架**
  - [x] 创建 `backend/main.py`
  - [x] 配置CORS中间件
  - [x] 注册路由模块
  - [x] 配置静态文件服务

- [x] **对话API路由**
  - [x] 创建 `backend/routers/chat.py`
  - [x] 定义 `ChatRequest` 和 `ChatResponse` 模型
  - [x] 实现 `POST /api/chat/message` 接口
  - [x] 实现 `POST /api/chat/new-session` 接口
  - [x] 添加参数验证和错误返回

- [x] **环境配置**
  - [x] 创建 `.env.example` 文件
  - [x] 编写 `backend/config.py` 配置加载模块
  - [x] 配置百炼API凭证
  - [x] 测试配置加载

- [x] **测试验证**
  - [x] 启动FastAPI服务（uvicorn）
  - [x] 使用curl测试 `/api/chat/message` 接口
  - [x] 测试多轮对话功能
  - [x] 测试错误场景（无效API Key等）
  - [x] 编写 `scripts/test_bailian.py` 自动化测试脚本

---

## ✅ Day 2：文本客服前端（已完成）

### 已完成

- [x] **HTML结构**
  - [x] 创建 `frontend/chat-widget.html`
  - [x] 设计聊天容器布局
  - [x] 添加消息显示区域
  - [x] 添加输入框和发送按钮
  - [x] 添加头部标题

- [x] **CSS样式**
  - [x] 设计聊天窗口样式（圆角、阴影）
  - [x] 设计消息气泡样式（用户/AI不同颜色）
  - [x] 设计头部样式（品牌色）
  - [x] 设计输入区域样式
  - [x] 添加响应式适配（移动端）

- [x] **JavaScript交互**
  - [x] 实现消息发送功能
  - [x] 实现消息显示功能（用户消息+AI回复）
  - [x] 实现多轮对话（维护session_id）
  - [x] 实现自动滚动到最新消息
  - [x] 添加动态loading效果
  - [x] 添加错误处理（网络错误、API错误）

- [x] **API对接**
  - [x] 配置API_BASE地址
  - [x] 实现fetch调用 `/api/chat/message`
  - [x] 处理响应数据
  - [x] 更新session_id
  - [x] 测试前后端联通

- [x] **UI优化**
  - [x] 添加欢迎消息
  - [x] 优化消息显示效果
  - [x] 添加输入框占位符
  - [x] 添加发送按钮hover效果
  - [x] 优化移动端显示
  - [x] 优化loading动画（脉冲效果）

- [x] **答案提取优化**
  - [x] 过滤思考过程
  - [x] 提取最终回答
  - [x] 清理引用标记

---

## ✅ Day 3：CCC电话API对接（已完成）

### 已完成

- [x] **CCC SDK研究**
  - [x] 阅读CCC Python SDK文档
  - [x] 了解MakeCall API调用方式
  - [x] 了解ListCallDetailRecords API
  - [x] 了解GetMonoRecording API

- [x] **CCC服务封装**
  - [x] 创建 `backend/services/aliyun_ccc.py`
  - [x] 实现 `CCCService` 类
  - [x] 实现 `make_call()` 方法（外呼）
  - [x] 实现 `list_call_records()` 方法（查询记录）
  - [x] 实现 `get_call_detail()` 方法（通话详情）
  - [x] 实现 `get_recording_url()` 方法（录音）
  - [x] 添加错误处理和日志记录

- [x] **外呼API**
  - [x] 创建 `backend/routers/ccc.py`
  - [x] 实现 `POST /api/ccc/outbound-call` 接口
  - [x] 添加参数验证（手机号格式）
  - [x] 返回call_id

- [x] **通话记录API**
  - [x] 实现 `GET /api/ccc/call-records` 接口
  - [x] 支持时间范围查询（start_time, end_time）
  - [x] 支持分页（page_number, page_size）
  - [x] 返回通话记录列表

- [x] **录音API**
  - [x] 实现 `GET /api/ccc/recording/{contact_id}` 接口
  - [x] 返回录音URL（302重定向）
  - [x] 处理录音不存在的情况

- [x] **测试验证**
  - [x] 配置CCC API凭证
  - [x] 测试外呼功能（拨打白名单手机号）
  - [x] 测试通话记录查询
  - [x] 测试录音获取

---

## ✅ Day 4：外呼管理前端（已完成）

### 已完成

- [x] **HTML结构**
  - [x] 创建 `frontend/outbound.html`
  - [x] 设计外呼表单（手机号输入框+拨打按钮）
  - [x] 设计通话记录表格
  - [x] 添加录音播放器区域

- [x] **CSS样式**
  - [x] 设计卡片式布局
  - [x] 设计表格样式
  - [x] 设计按钮样式（拨打按钮醒目）
  - [x] 设计状态标签（已完成/未接听/通话中）
  - [x] 添加响应式适配

- [x] **JavaScript交互**
  - [x] 实现外呼功能（调用 `/api/ccc/outbound-call`）
  - [x] 实现通话记录加载（调用 `/api/ccc/call-records`）
  - [x] 实现录音播放功能（动态加载URL）
  - [x] 添加拨打状态提示
  - [x] 添加错误处理

- [x] **API对接**
  - [x] 配置API_BASE地址
  - [x] 对接外呼API
  - [x] 对接通话记录API
  - [x] 对接录音API
  - [x] 测试前后端联通

- [x] **状态映射完善**
  - [x] 添加所有状态的中文映射
  - [x] 添加状态标签颜色

---

## ️ Day 5：数据库 + 客户管理（部分完成）

### 已完成

- [x] **客户管理API**
  - [x] 创建 `backend/routers/customers.py`
  - [x] 实现 `GET /api/customers/` 接口（列表）
  - [x] 实现 `GET /api/customers/{id}` 接口（详情）
  - [x] 实现 `POST /api/customers/` 接口（创建）
  - [x] 实现 `PUT /api/customers/{id}` 接口（更新）
  - [x] 实现 `DELETE /api/customers/{id}` 接口（删除）

- [x] **客户管理前端**
  - [x] 创建 `frontend/customers.html`
  - [x] 编写HTML结构（表格+表单）
  - [x] 编写CSS样式
  - [x] 编写JavaScript交互（增删改查）
  - [x] 对接客户管理API

### 未完成

- [x] **数据库设计** ✅ 今日完成
  - [x] 设计 customers 表（客户信息）
  - [x] 设计 call_records 表（通话记录）
  - [x] 设计 appointments 表（预约信息）
  - [x] 设计 chat_sessions 表（文本对话会话）
  - [x] 设计 chat_messages 表（文本对话消息）
  - [x] 编写SQLAlchemy模型（使用ORM替代SQL脚本）

- [x] **SQLAlchemy模型** ✅ 今日完成
  - [x] 创建 `backend/models/database.py`
  - [x] 实现 Customer 模型
  - [x] 实现 CallRecord 模型
  - [x] 实现 Appointment 模型
  - [x] 实现 ChatSession 模型
  - [x] 实现 ChatMessage 模型
  - [x] 配置数据库连接

- [x] **数据库初始化** ✅ 今日完成
  - [x] 编写 `scripts/init_db.py`
  - [x] 创建所有表
  - [x] 添加测试数据
  - [x] 测试数据库连接

- [x] **通话记录自动保存** ✅ 今日完成
  - [x] 修改 `routers/ccc.py`
  - [x] 外呼前自动创建通话记录
  - [x] 关联客户（根据手机号查找或创建）
  - [x] 客户不存在时自动创建

---

##  Day 6：Webhook + 全流程联调（未完成）

### 未完成

- [x] **Webhook实现** ✅ 今日完成
  - [x] 创建 `backend/routers/webhook.py`
  - [x] 实现 `POST /api/webhook/ccc/call-ended` 接口
  - [x] 解析CCC回调数据
  - [x] 自动更新通话记录到数据库
  - [x] 保存录音URL
  - [x] 关联客户通话历史

- [ ] **CCC Webhook配置**
  - [ ] 登录CCC控制台
  - [ ] 配置Webhook回调地址
  - [ ] 测试回调是否能正常接收

- [ ] **全流程联调**
  - [x] 文本客服完整测试 ✅
  - [x] AI外呼完整测试 ✅
  - [ ] AI接听测试（需要配置AI接听）

- [ ] **Bug修复**
  - [x] 修复录音播放问题 ✅
  - [x] 优化答案提取逻辑 ✅
  - [ ] 优化响应速度

---

## ️ Day 7：优化 + 演示准备（进行中）

### 已完成

- [x] **UI优化**
  - [x] 优化loading动画（脉冲效果）
  - [x] 优化答案提取逻辑

### 未完成

- [ ] **错误处理**
  - [ ] 完善API错误提示
  - [ ] 添加网络错误处理
  - [ ] 添加空数据提示
  - [ ] 添加操作确认对话框

- [x] **文档编写** ✅ 今日完成
  - [x] 编写 README.md（300+行）
  - [x] 项目介绍
  - [x] 功能说明
  - [x] 安装部署步骤
  - [x] 配置说明
  - [x] 使用示例
  - [ ] FAQ

- [ ] **演示准备**
  - [ ] 编写演示脚本（演示流程）
  - [ ] 准备演示话术
  - [ ] 准备演示数据（测试客户、测试通话记录）
  - [ ] 演示环境检查

---

## 📊 总体进度

| 阶段 | 状态 | 完成度 |
|---|---|---|
| Day 0: 前置准备 | ✅ 完成 | 100% |
| Day 1: 基础搭建 | ✅ 完成 | 100% |
| Day 2: 文本客服 | ✅ 完成 | 100% |
| Day 3: CCC电话API | ✅ 完成 | 100% |
| Day 4: 外呼管理 | ✅ 完成 | 100% |
| Day 5: 客户管理 | ️ 部分完成 | 60% |
| Day 6: 全流程联调 | ❌ 未开始 | 30% |
| Day 7: 优化演示 | ️ 进行中 | 20% |

**总体完成度：约 70%**

---

## 🎯 今天（2026-09-15）应该完成

### 上午（09:00-12:00）
1. **数据库实现**（高优先级）
   - 设计表结构
   - 创建SQLAlchemy模型
   - 编写数据库初始化脚本
   - 替换内存存储为数据库存储

2. **客户管理完善**（高优先级）
   - 完善客户详情页面
   - 添加客户通话记录查询

### 下午（13:00-18:00）
3. **通话记录自动保存**（高优先级）
   - 修改外呼流程，自动保存记录

4. **Webhook实现**（中优先级）
   - 创建webhook路由
   - 实现通话结果回调处理

5. **文档编写**（低优先级）
   - 编写README.md
   - 准备演示脚本

---

**文档版本**：v4.0  
**最后更新**：2026-09-15  
**状态**：进行中
