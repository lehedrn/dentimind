# 坐席状态管理功能说明

> 更新时间：2026-09-15  
> 版本：v1.1

---

## 📋 功能概述

电话外呼功能现已支持**坐席状态自动检查和自动签到**，解决了之前"不知道坐席是否在线"的问题。

### 核心改进

1. **外呼前自动检查坐席状态**
2. **坐席不在线时自动签到**
3. **提供API手动查询和控制坐席状态**

---

## 🔧 功能详解

### 1. 自动检查坐席状态

**触发时机**：每次发起外呼前

**检查流程**：
```
发起外呼请求
  ↓
检查坐席状态
  ↓
坐席在线？
  ├─ 是 → 继续外呼
  └─ 否 → 自动签到
           ↓
        签到成功？
          ├─ 是 → 继续外呼
          └─ 否 → 返回错误
```

**坐席状态说明**：
- `Online` / `Ready` - 在线，可以接听
- `NotReady` - 在线，但忙碌中
- `Break` - 在线，休息中
- `Offline` - 离线
- `Unknown` - 状态未知

**判断逻辑**：
- 状态为 `Online`、`Ready`、`NotReady`、`Break` → **视为在线**
- 其他状态 → **视为不在线**

---

### 2. 自动签到坐席

**触发条件**：
- 坐席状态为不在线
- `auto_sign_in` 参数为 `true`（默认）

**签到流程**：
1. 检测到坐席不在线
2. 调用CCC API签到接口
3. 等待1秒让签到生效
4. 再次检查坐席状态
5. 返回签到结果

**签到结果**：
```json
{
  "is_online": true,
  "agent_status": "Ready",
  "action_taken": "auto_sign_in",
  "success": true,
  "message": "坐席已自动签到"
}
```

---

### 3. 手动控制API

提供了3个API接口，方便前端展示和控制坐席状态。

#### API 1: 查询坐席状态

**请求**：
```http
GET /api/ccc/agent/status
```

**响应**：
```json
{
  "success": true,
  "agent_status": "Ready",
  "is_online": true,
  "user_id": "智天气@demo-1767693362317534",
  "device_id": "device"
}
```

**使用场景**：
- 前端页面显示坐席状态指示灯
- 定期检查坐席状态
- 外呼前预检查

---

#### API 2: 手动签到坐席

**请求**：
```http
POST /api/ccc/agent/sign-in
```

**响应**：
```json
{
  "success": true,
  "message": "坐席签到成功",
  "user_id": "智天气@demo-1767693362317534"
}
```

**使用场景**：
- 手动控制坐席上线
- 自动签到失败时手动重试
- 管理坐席工作状态

---

#### API 3: 确保坐席在线

**请求**：
```http
POST /api/ccc/agent/ensure-online?auto_sign_in=true
```

**响应**：
```json
{
  "is_online": true,
  "agent_status": "Ready",
  "action_taken": "auto_sign_in",
  "success": true,
  "message": "坐席已自动签到"
}
```

**参数**：
- `auto_sign_in` - 如果不在线，是否自动签到（默认：true）

**使用场景**：
- 外呼前确保坐席在线
- 批量外呼前批量签到
- 自动化脚本调用

---

## 🎯 外呼流程优化

### 之前的流程（有问题）

```
用户点击"拨打"
  ↓
直接调用CCC外呼API
  ↓
❌ 坐席不在线 → 外呼失败
```

**问题**：
- 不知道坐席是否在线
- 坐席不在线时外呼失败
- 没有自动恢复机制

---

### 现在的流程（已优化）

```
用户点击"拨打"
  ↓
检查坐席状态
  ↓
坐席在线？
  ├─ 是 → 调用CCC外呼API → 外呼成功 ✅
  └─ 否 → 自动签到
           ↓
        签到成功？
          ├─ 是 → 调用CCC外呼API → 外呼成功 ✅
          └─ 否 → 返回错误提示 ❌
```

**优势**：
- ✅ 自动检查坐席状态
- ✅ 坐席不在线时自动恢复
- ✅ 提高外呼成功率
- ✅ 减少人工干预

---

## 📊 外呼响应增强

### 新的外呼响应格式

```json
{
  "call_id": "job-xxxxx",
  "contact_id": "channel-xxxxx",
  "job_id": "job-xxxxx",
  "channel_id": "channel-xxxxx",
  "status": "initiated",
  "success": true,
  "agent_status": {
    "is_online": true,
    "agent_status": "Ready",
    "action_taken": "auto_sign_in",
    "success": true,
    "message": "坐席已自动签到"
  }
}
```

**新增字段**：
- `agent_status` - 坐席状态信息
  - `is_online` - 是否在线
  - `agent_status` - 具体状态
  - `action_taken` - 采取的操作
    - `none` - 坐席已在线，无需操作
    - `auto_sign_in` - 自动签到成功
    - `auto_sign_in_failed` - 自动签到失败
  - `success` - 操作是否成功
  - `message` - 操作说明

---

## 🔍 错误处理

### 场景1: 坐席不在线且自动签到失败

**错误信息**：
```
坐席不在线，无法发起外呼。坐席签到失败: [具体错误]
```

**可能原因**：
- CCC配置错误
- 网络连接问题
- 坐席账号权限问题
- CCC实例未开通

**解决方法**：
1. 检查CCC配置（环境变量）
2. 检查网络连接
3. 登录CCC控制台检查坐席配置
4. 手动调用签到API查看详细错误

---

### 场景2: 外呼时坐席状态异常

**错误信息**：
```
坐席不在线，无法发起外呼。
```

**可能原因**：
- 自动签到后坐席仍不在线
- 坐席被其他操作置为离线

**解决方法**：
1. 调用 `/api/ccc/agent/status` 查看详细状态
2. 调用 `/api/ccc/agent/sign-in` 手动签到
3. 检查CCC控制台坐席状态
4. 确认坐席账号配置正确

---

## 💡 最佳实践

### 1. 前端展示坐席状态

**建议**：在外呼管理页面显示坐席状态指示灯

```html
<!-- 示例代码 -->
<div class="agent-status">
  <span class="status-indicator" id="status-indicator"></span>
  <span id="status-text">检查中...</span>
  <button onclick="checkAgentStatus()">刷新状态</button>
  <button onclick="signInAgent()" id="sign-in-btn">手动签到</button>
</div>

<script>
async function checkAgentStatus() {
  const response = await fetch('/api/ccc/agent/status');
  const data = await response.json();
  
  const indicator = document.getElementById('status-indicator');
  const text = document.getElementById('status-text');
  const signBtn = document.getElementById('sign-in-btn');
  
  if (data.is_online) {
    indicator.className = 'status-indicator online';
    text.textContent = `坐席在线 (${data.agent_status})`;
    signBtn.style.display = 'none';
  } else {
    indicator.className = 'status-indicator offline';
    text.textContent = '坐席离线';
    signBtn.style.display = 'inline-block';
  }
}

async function signInAgent() {
  const response = await fetch('/api/ccc/agent/sign-in', {
    method: 'POST'
  });
  const data = await response.json();
  
  if (data.success) {
    alert('签到成功');
    checkAgentStatus();
  } else {
    alert('签到失败: ' + data.message);
  }
}

// 页面加载时检查状态
checkAgentStatus();
</script>
```

---

### 2. 批量外呼前预检查

**场景**：批量外呼多个客户

**建议流程**：
```
1. 调用 ensure-online API 确保坐席在线
2. 如果失败，提示用户并停止
3. 如果成功，开始批量外呼
4. 每个外呼间隔适当时间（避免频率限制）
```

**示例代码**：
```python
import requests

# 确保坐席在线
response = requests.post(
    'http://localhost:8000/api/ccc/agent/ensure-online',
    params={'auto_sign_in': True}
)
result = response.json()

if not result['is_online']:
    print(f"坐席不在线: {result['message']}")
    exit(1)

print(f"坐席已在线: {result['agent_status']}")

# 批量外呼
phone_numbers = ['13800138001', '13800138002', '13800138003']
for phone in phone_numbers:
    response = requests.post(
        'http://localhost:8000/api/ccc/outbound-call',
        params={'callee_number': phone}
    )
    result = response.json()
    print(f"外呼 {phone}: {result.get('status')}")
    
    # 间隔2秒，避免频率限制
    time.sleep(2)
```

---

### 3. 定期检查坐席状态

**场景**：长时间运行的系统

**建议**：定期检查坐席状态，确保坐席保持在线

```python
import requests
import time

def monitor_agent_status():
    while True:
        response = requests.get('http://localhost:8000/api/ccc/agent/status')
        result = response.json()
        
        if not result['is_online']:
            print(f"⚠️ 坐席离线: {result['agent_status']}")
            
            # 尝试自动签到
            sign_response = requests.post(
                'http://localhost:8000/api/ccc/agent/sign-in'
            )
            sign_result = sign_response.json()
            
            if sign_result['success']:
                print("✅ 坐席已自动签到")
            else:
                print(f"❌ 自动签到失败: {sign_result['message']}")
        else:
            print(f"✅ 坐席在线: {result['agent_status']}")
        
        # 每5分钟检查一次
        time.sleep(300)

monitor_agent_status()
```

---

## 🧪 测试指南

### 测试1: 查询坐席状态

```bash
curl http://localhost:8000/api/ccc/agent/status
```

**预期结果**：
- 返回坐席状态信息
- `is_online` 为 true 或 false

---

### 测试2: 手动签到坐席

```bash
curl -X POST http://localhost:8000/api/ccc/agent/sign-in
```

**预期结果**：
- 坐席签到成功
- `success` 为 true

---

### 测试3: 外呼前自动检查

```bash
# 先确保坐席在线
curl -X POST "http://localhost:8000/api/ccc/agent/ensure-online?auto_sign_in=true"

# 然后发起外呼
curl -X POST "http://localhost:8000/api/ccc/outbound-call?callee_number=13800138000"
```

**预期结果**：
- 外呼成功
- 响应中包含 `agent_status` 信息
- `action_taken` 显示采取的操作

---

### 测试4: 模拟坐席离线

**步骤**：
1. 登录CCC控制台，手动将坐席置为离线
2. 发起外呼请求
3. 观察日志和响应

**预期结果**：
- 系统检测到坐席离线
- 自动尝试签到
- 签到成功后继续外呼
- 日志记录整个过程

---

## 📈 监控和日志

### 关键日志

系统会在以下情况记录日志：

```
INFO - 发起外呼前检查坐席状态...
INFO - 检查坐席状态 - user_id: xxx
INFO - 坐席状态检查完成 - state: Ready, is_online: True
INFO - 坐席在线，准备发起外呼 - status: Ready
INFO - 外呼成功 - call_id: xxx, agent_action: none

WARNING - 坐席不在线 - status: Offline
INFO - 坐席不在线，尝试自动签到...
INFO - 签到坐席 - user_id: xxx, device_id: device
INFO - 坐席签到成功 - user_id: xxx
INFO - 外呼成功 - call_id: xxx, agent_action: auto_sign_in
```

### 监控指标

建议监控以下指标：
- 坐席在线率
- 自动签到成功率
- 外呼成功率
- 平均外呼耗时

---

## 🔮 未来优化方向

### 1. 坐席状态WebSocket推送

**现状**：前端需要轮询查询坐席状态

**优化**：使用WebSocket实时推送坐席状态变化

**优势**：
- 实时性更好
- 减少API调用
- 提升用户体验

---

### 2. 多坐席支持

**现状**：只支持单个坐席

**优化**：
- 支持多个坐席
- 坐席负载均衡
- 坐席队列管理

**场景**：
- 大型呼叫中心
- 多客服人员协作
- 智能分配外呼任务

---

### 3. 坐席状态持久化

**现状**：坐席状态由CCC管理

**优化**：
- 本地缓存坐席状态
- 记录坐席状态历史
- 分析坐席在线模式

**价值**：
- 优化坐席排班
- 预测坐席可用性
- 提升运营效率

---

### 4. 智能签到策略

**现状**：外呼前检查并签到

**优化**：
- 定时签到（工作时间自动签到）
- 智能预签到（预测外呼高峰）
- 坐席健康检查

**优势**：
- 减少外呼延迟
- 提高坐席可用性
- 降低失败率

---

## 📞 技术支持

如有问题，请查看：
- [FAQ文档](./faq.md) - 常见问题解答
- [系统功能状态](./system-capability-status.md) - 功能说明
- [操作手册](./manual-test-guide.md) - 操作指南

---

**更新时间**：2026-09-15  
**版本**：v1.1  
**维护团队**：口腔医院AI客服系统开发团队
