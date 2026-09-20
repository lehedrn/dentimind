# 日志系统使用指南

> 更新时间：2026-09-15  
> 版本：v2.0（完整日志版）

---

## 📋 日志系统概述

系统现已配置**完整的日志记录**，支持开发阶段的详细调试。

### 日志特性

✅ **分级日志** - DEBUG/INFO/WARNING/ERROR  
✅ **多文件输出** - 应用日志、错误日志、访问日志分离  
✅ **日志轮转** - 自动清理旧日志，节省磁盘空间  
✅ **彩色控制台** - 开发时便于查看  
✅ **详细请求日志** - 记录每个HTTP请求和响应  
✅ **异常堆栈** - 完整的错误追踪信息  

---

## 📁 日志文件说明

### 日志位置

```
/home/workspaces/com/ztq/dentimind/logs/
├── app.log        # 应用日志（所有级别）
├── error.log      # 错误日志（仅ERROR及以上）
└── access.log     # 访问日志（HTTP请求）
```

### 1. app.log - 应用日志

**内容**：所有级别的日志（DEBUG/INFO/WARNING/ERROR）

**用途**：
- 开发调试
- 功能追踪
- 系统运行状态

**示例**：
```
2026-09-15 18:00:00 | INFO     | main                   | → POST /api/chat/message - 客户端: 127.0.0.1
2026-09-15 18:00:00 | INFO     | routers.chat           | 收到对话请求 - session_id: xxx, message: 你好...
2026-09-15 18:00:01 | DEBUG    | services.bailian_chat  | 调用百炼API - session_id: xxx, prompt: 你好
2026-09-15 18:00:06 | DEBUG    | services.bailian_chat  | 百炼API响应成功 - 响应长度: 150
2026-09-15 18:00:06 | INFO     | routers.chat           | 对话响应成功 - session_id: xxx, reply长度: 150
2026-09-15 18:00:06 | INFO     | main                   | ← POST /api/chat/message - 状态: 200 - 耗时: 6.123s
```

**轮转策略**：
- 文件大小：10MB
- 保留数量：10个备份
- 总容量：110MB

---

### 2. error.log - 错误日志

**内容**：仅ERROR及以上级别（ERROR/CRITICAL）

**用途**：
- 快速定位问题
- 监控系统健康
- 异常分析

**示例**：
```
2026-09-15 18:05:00 | ERROR    | routers.ccc            | 外呼失败: 坐席不在线
Traceback (most recent call last):
  File "/path/to/ccc.py", line 71, in make_outbound_call
    result = await ccc_service.make_call(callee_number)
  File "/path/to/aliyun_ccc.py", line 150, in make_call
    raise Exception("坐席不在线，无法发起外呼")
Exception: 坐席不在线，无法发起外呼
```

**轮转策略**：
- 文件大小：10MB
- 保留数量：10个备份
- 总容量：110MB

---

### 3. access.log - 访问日志

**内容**：所有HTTP请求的访问记录

**用途**：
- 访问统计分析
- 性能监控
- 安全审计

**示例**：
```
2026-09-15 18:00:00 | INFO     | uvicorn.access         | 127.0.0.1:54321 - "POST /api/chat/message HTTP/1.1" 200
2026-09-15 18:00:01 | INFO     | uvicorn.access         | 127.0.0.1:54322 - "GET /api/customers/ HTTP/1.1" 200
2026-09-15 18:00:02 | INFO     | uvicorn.access         | 127.0.0.1:54323 - "POST /api/ccc/outbound-call HTTP/1.1" 200
```

**轮转策略**：
- 按天轮转（每天午夜）
- 保留30天
- 总容量：约30个文件

---

## 🔍 查看日志

### 方法1: 使用service.sh脚本

```bash
# 查看实时日志（所有日志）
./service.sh logs

# 查看最近日志（状态命令）
./service.sh status

# 查看错误日志
./service.sh errors
```

---

### 方法2: 使用tail命令

```bash
# 实时查看应用日志
tail -f logs/app.log

# 实时查看错误日志
tail -f logs/error.log

# 实时查看访问日志
tail -f logs/access.log

# 查看最近100行
tail -100 logs/app.log

# 查看最近1小时的日志
find logs/ -name "*.log" -mmin -60 -exec tail -f {} +
```

---

### 方法3: 使用grep过滤

```bash
# 查找错误
grep -i "error" logs/app.log

# 查找特定会话
grep "session-123456" logs/app.log

# 查找特定API
grep "/api/chat" logs/app.log

# 查找特定时间段的日志
grep "2026-09-15 18:" logs/app.log

# 查找慢请求（耗时>1秒）
grep "耗时: [1-9]" logs/app.log
```

---

### 方法4: 使用less查看

```bash
# 查看日志（支持搜索）
less logs/app.log

# 搜索（在less中按/然后输入关键词）
/error
/session-123

# 退出（按q）
```

---

## 📊 日志级别说明

### DEBUG（调试）

**用途**：详细的调试信息

**包含内容**：
- 完整的请求/响应内容
- API调用细节
- 变量值追踪
- 函数调用链

**示例**：
```
DEBUG | services.bailian_chat | 调用百炼API - session_id: xxx, prompt: 你好
DEBUG | services.bailian_chat | 百炼API响应: {"status": 200, "data": {...}}
DEBUG | routers.chat | 完整请求内容: session_id=xxx, message=你好
```

**使用场景**：
- 开发阶段
- 问题排查
- 功能调试

---

### INFO（信息）

**用途**：正常的操作信息

**包含内容**：
- 请求开始/结束
- 操作成功
- 状态变化
- 重要事件

**示例**：
```
INFO | main | 服务启动成功 - http://0.0.0.0:8000
INFO | routers.chat | 收到对话请求 - session_id: xxx, message: 你好...
INFO | routers.chat | 对话响应成功 - session_id: xxx, reply长度: 150
INFO | main | ← POST /api/chat/message - 状态: 200 - 耗时: 6.123s
```

**使用场景**：
- 生产环境
- 日常监控
- 操作审计

---

### WARNING（警告）

**用途**：潜在的问题

**包含内容**：
- 配置问题
- 非致命错误
- 资源不足
- 异常但不影响功能

**示例**：
```
WARNING | config | 配置验证失败: 缺少CCC_INSTANCE_ID
WARNING | services.bailian_chat | 百炼API响应较慢: 8.5秒
WARNING | routers.customers | 客户不存在，自动创建
```

**使用场景**：
- 需要关注但不影响功能
- 可能需要优化

---

### ERROR（错误）

**用途**：严重的错误

**包含内容**：
- 操作失败
- 异常堆栈
- 功能不可用
- 需要立即处理

**示例**：
```
ERROR | routers.ccc | 外呼失败: 坐席不在线
Traceback (most recent call last):
  File "ccc.py", line 71, in make_outbound_call
    result = await ccc_service.make_call(callee_number)
Exception: 坐席不在线，无法发起外呼

ERROR | services.bailian_chat | 百炼API调用失败: Connection timeout
```

**使用场景**：
- 功能异常
- 需要立即修复
- 用户受影响

---

### CRITICAL（严重）

**用途**：系统级严重错误

**包含内容**：
- 系统崩溃
- 核心功能失效
- 数据丢失风险

**示例**：
```
CRITICAL | main | 数据库初始化失败，无法启动
CRITICAL | main | 配置验证失败，必需的配置缺失
```

**使用场景**：
- 系统无法运行
- 需要紧急处理

---

## 🛠️ 日志配置

### 环境变量配置

在 `.env` 文件中配置：

```bash
# 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
LOG_LEVEL=DEBUG

# 日志目录
LOG_DIR=./logs
```

### 日志级别调整

**开发阶段**（当前）：
```bash
LOG_LEVEL=DEBUG  # 记录所有详细信息
```

**生产环境**：
```bash
LOG_LEVEL=INFO   # 只记录重要信息
```

**问题排查时**：
```bash
LOG_LEVEL=DEBUG  # 临时调整为DEBUG
```

---

## 📝 日志格式说明

### 标准格式

```
时间戳 | 日志级别 | 模块名称 | 日志内容
```

**示例**：
```
2026-09-15 18:00:00 | INFO     | routers.chat           | 收到对话请求 - session_id: xxx
```

**各字段说明**：
- **时间戳**：`YYYY-MM-DD HH:MM:SS`
- **日志级别**：DEBUG/INFO/WARNING/ERROR/CRITICAL
- **模块名称**：日志记录器名称（最长20字符）
- **日志内容**：具体的日志信息

---

### HTTP请求日志格式

```
→ 方法 URL - 客户端: IP    # 请求开始
← 方法 URL - 状态: 状态码 - 耗时: 秒数 - 客户端: IP    # 请求结束
✗ 方法 URL - 异常: 错误信息 - 耗时: 秒数 - 客户端: IP    # 请求异常
```

**示例**：
```
→ POST /api/chat/message - 客户端: 127.0.0.1
← POST /api/chat/message - 状态: 200 - 耗时: 6.123s - 客户端: 127.0.0.1

→ POST /api/ccc/outbound-call - 客户端: 127.0.0.1
✗ POST /api/ccc/outbound-call - 异常: 坐席不在线 - 耗时: 0.523s - 客户端: 127.0.0.1
```

---

## 🔧 常见问题

### Q1: 日志文件在哪里？

**A**: 在项目根目录的 `logs/` 文件夹下：
```
/home/workspaces/com/ztq/dentimind/logs/
├── app.log
├── error.log
└── access.log
```

---

### Q2: 为什么看不到DEBUG日志？

**A**: 检查日志级别配置：
```bash
# 查看当前配置
grep LOG_LEVEL .env

# 修改为DEBUG
echo "LOG_LEVEL=DEBUG" >> .env

# 重启服务
./service.sh restart
```

---

### Q3: 日志文件太大了怎么办？

**A**: 系统已配置自动轮转：
- `app.log` 和 `error.log`：10MB自动轮转，保留10个备份
- `access.log`：按天轮转，保留30天

如果需要手动清理：
```bash
# 清空日志文件（不删除文件）
> logs/app.log
> logs/error.log
> logs/access.log
```

---

### Q4: 如何只查看错误日志？

**A**: 查看 `error.log` 文件：
```bash
# 实时查看
tail -f logs/error.log

# 查看最近100行
tail -100 logs/error.log

# 使用service.sh
./service.sh errors
```

---

### Q5: 如何搜索特定会话的日志？

**A**: 使用grep：
```bash
# 搜索特定session_id
grep "session-123456" logs/app.log

# 搜索特定客户的电话
grep "13800138000" logs/app.log

# 搜索特定时间段
grep "2026-09-15 18:" logs/app.log
```

---

### Q6: 日志太多，如何过滤？

**A**: 使用grep过滤：
```bash
# 只看INFO级别
grep "| INFO" logs/app.log

# 只看WARNING和ERROR
grep -E "| WARNING| ERROR" logs/app.log

# 排除DEBUG
grep -v "| DEBUG" logs/app.log

# 只看特定API
grep "/api/chat" logs/app.log
```

---

### Q7: 如何实时查看所有日志？

**A**: 使用tail -f：
```bash
# 查看应用日志
tail -f logs/app.log

# 同时查看多个日志
tail -f logs/*.log

# 使用service.sh
./service.sh logs
```

---

### Q8: 日志文件损坏了怎么办？

**A**: 直接删除，重启服务会自动创建：
```bash
# 停止服务
./service.sh stop

# 删除损坏的日志
rm logs/*.log

# 启动服务
./service.sh start
```

---

### Q9: 如何调整日志级别而不重启？

**A**: 目前不支持动态调整，需要重启服务：
```bash
# 修改配置
sed -i 's/LOG_LEVEL=.*/LOG_LEVEL=DEBUG/' .env

# 重启服务
./service.sh restart
```

---

### Q10: 日志占用太多磁盘空间怎么办？

**A**: 
1. **调整轮转策略**（修改 `logging_config.py`）：
```python
MAX_BYTES = 5 * 1024 * 1024  # 改为5MB
BACKUP_COUNT = 5              # 保留5个备份
```

2. **定期清理**：
```bash
# 删除7天前的日志
find logs/ -name "*.log.*" -mtime +7 -delete

# 清空当前日志
> logs/app.log
```

3. **使用日志管理工具**（如logrotate）

---

## 📊 日志分析技巧

### 1. 统计错误数量

```bash
# 统计ERROR数量
grep -c "| ERROR" logs/app.log

# 统计今天的错误
grep "$(date +%Y-%m-%d)" logs/app.log | grep -c "| ERROR"
```

---

### 2. 找出慢请求

```bash
# 找出耗时>5秒的请求
grep "耗时: [5-9]\." logs/app.log

# 找出最慢的10个请求
grep "耗时:" logs/app.log | sort -t':' -k3 -nr | head -10
```

---

### 3. 统计API调用次数

```bash
# 统计各API调用次数
grep "POST\|GET" logs/access.log | awk '{print $5}' | sort | uniq -c | sort -rn
```

---

### 4. 找出频繁错误

```bash
# 统计错误类型
grep "| ERROR" logs/app.log | awk -F'|' '{print $4}' | sort | uniq -c | sort -rn
```

---

## 🚀 最佳实践

### 开发阶段

1. **使用DEBUG级别** - 记录所有细节
2. **实时监控日志** - `tail -f logs/app.log`
3. **关注错误日志** - 及时发现和修复问题
4. **定期查看日志** - 了解系统运行状态

### 生产环境

1. **使用INFO级别** - 减少日志量
2. **监控错误日志** - 设置告警
3. **定期轮转清理** - 节省磁盘空间
4. **保留关键日志** - 便于问题追踪

### 问题排查

1. **先查看error.log** - 快速定位错误
2. **使用grep过滤** - 缩小范围
3. **查看完整堆栈** - 理解问题根源
4. **临时调整DEBUG** - 获取更多细节

---

## 📞 技术支持

如有日志相关问题，请查看：
- [FAQ文档](./faq.md) - 常见问题解答
- [操作手册](./manual-test-guide.md) - 操作指南

---

**更新时间**：2026-09-15  
**版本**：v2.0  
**维护团队**：口腔医院AI客服系统开发团队
