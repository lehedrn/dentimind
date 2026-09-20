# 呼入功能修复报告 - 2026-09-16

## ✅ 已完成的工作

### 1. 数据库模型修复
**问题**: `CallRecord` 缺少 `caller_number` 和 `direction` 字段,无法正确记录呼入通话

**修复**:
- 添加 `caller_number` 字段(String 30):存储主叫号码
- 添加 `direction` 字段(String 20):存储通话方向(inbound/outbound)
- 添加自动迁移逻辑,为现有数据库添加新字段
- 更新 `to_dict()` 方法,添加 `call_type` 字段兼容前端

**文件**: `backend/models/database.py`

### 2. Webhook 逻辑重写
**问题**: 原逻辑只用 `callee_number` 查找客户,对呼入场景错误(呼入时客户是 caller)

**修复**:
- 实现智能方向检测:
  - 优先使用 CCC 显式提供的 `direction`/`call_type` 字段
  - 否则通过号码推断:caller 是系统 DID → outbound;callee 是系统 DID → inbound
- 根据方向正确匹配客户:
  - 呼入:客户 = `caller_number`
  - 呼出:客户 = `callee_number`
- 同时记录 `caller_number` 和 `callee_number`
- 自动创建客户时使用正确的客户号码

**文件**: `backend/routers/webhook.py`

### 3. CCC call_id 提取 bug 修复
**问题**: 外呼时 `call_id` 字段存储了整个 CCC API 响应体(字符串),而非真实的 job_id

**原因**: CCC SDK 返回 PascalCase 属性(Data.CallContext.JobId),但代码用 snake_case 访问(data.call_context.job_id)

**修复**:
- 同时支持 snake_case 和 PascalCase 属性访问
- 添加正则表达式回退:从字符串表示中提取 JobId
- 最后兜底:使用 RequestId 或生成 UUID,绝不存整个响应体
- 外呼路由添加防御:如果 call_id 包含 JSON 特征(长度>100或以`{`开头),拒绝存储

**文件**: `backend/services/aliyun_ccc.py`, `backend/routers/ccc.py`

### 4. 外呼路由更新
**修复**:
- 创建初始通话记录时设置 `direction="outbound"` 和 `caller_number=SYSTEM_DID`
- 更健壮的 call_id/contact_id 赋值逻辑

**文件**: `backend/routers/ccc.py`

### 5. 数据库清理
**修复**: 清理了 2 条 call_id 存储了整个响应体的错误记录,从字符串中提取了真实的 job_id

### 6. 完整测试验证
**测试场景**:
1. ✅ 呼入(新客户):自动创建客户并关联
2. ✅ 呼入(老客户):匹配已有客户
3. ✅ 呼入(显式 direction 字段):正确识别
4. ✅ 呼出回调更新:正确更新已有记录
5. ✅ API 返回格式:正确返回 `call_type: "Inbound"/"Outbound"`

**测试数据**:
- 创建了 4 条测试通话记录(2 条呼入新客户,1 条呼入老客户,1 条显式 direction)
- 验证了数据库字段正确存储
- 验证了客户关联正确

---

## 📋 剩余工作(需要人工完成)

### 1. 阿里云 CCC 控制台配置(必须)
**步骤**:
1. 登录阿里云 CCC 控制台
2. 配置呼入号码绑定(将 DID 号码 66905712367967212 绑定到实例)
3. 配置呼入路由(将来电路由到坐席)
4. 配置 Webhook 地址(通话结束回调 URL)
   - URL 格式: `http://<your-domain>/api/webhook/ccc/call-ended`
   - 需要 CCC 能访问到这个地址(如果是本地测试,需要内网穿透或部署到公网)

### 2. 真实电话测试(必须)
**测试流程**:
1. 用测试手机拨打 DID 号码(66905712367967212)
2. 人工接听通话
3. 挂断后检查:
   - 日志: `backend/logs/app.log` 应显示 "收到CCC通话结束回调"
   - 数据库: `call_records` 表应有新记录,`direction="inbound"`
   - 前端: `http://localhost:8000/customers` → 查看客户 → 通话记录应显示"呼入"
   - 录音: 如果有录音,应能播放

### 3. 可选优化
- **前端改进**: 客户通话记录页面的"被叫号码"列对呼入显示系统 DID,可能令人困惑。可以改为显示"对方号码"或隐藏该列
- **Webhook 安全**: 添加签名验证,防止未授权请求
- **错误处理**: 完善 CCC API 调用失败的错误提示

---

## 🔧 技术细节

### 通话方向检测逻辑
```python
def detect_call_direction(callback_data, caller_number, callee_number):
    # 1. 显式字段优先
    for key in ("direction", "call_direction", "call_type", "CallType"):
        val = callback_data.get(key)
        if val:
            val_lower = str(val).lower()
            if val_lower in ("inbound", "in", "incoming"):
                return "inbound"
            if val_lower in ("outbound", "out", "outgoing"):
                return "outbound"
    
    # 2. 号码推断
    SYSTEM_DID = os.getenv("CCC_CALLER_NUMBER")
    if SYSTEM_DID:
        if caller_number == SYSTEM_DID:
            return "outbound"  # 系统打出
        if callee_number == SYSTEM_DID:
            return "inbound"   # 客户打入
    
    return "outbound"  # 默认
```

### 客户匹配逻辑
```python
def get_customer_phone(direction, caller_number, callee_number):
    if direction == "inbound":
        return caller_number  # 呼入:客户是拨打方
    else:
        return callee_number  # 呼出:客户是被叫方
```

### CCC call_id 提取逻辑
```python
# 1. 尝试属性访问(snake_case + PascalCase)
data = getattr(body, "data", None) or getattr(body, "Data", None)
if data:
    ctx = getattr(data, "call_context", None) or getattr(data, "CallContext", None)
    if ctx:
        job_id = getattr(ctx, "job_id", None) or getattr(ctx, "JobId", None)

# 2. 正则回退
if not job_id:
    import re
    body_str = str(body)
    m = re.search(r"[Jj]ob[Ii]d['\":\s=]+([A-Za-z0-9_\-]+)", body_str)
    if m:
        job_id = m.group(1)

# 3. 最后兜底
if not job_id:
    rid = getattr(body, "request_id", None) or getattr(body, "RequestId", None)
    job_id = rid or f"call-{uuid.uuid4().hex[:12]}"
```

---

## 📊 数据库变更

### 新增字段
```sql
ALTER TABLE call_records ADD COLUMN caller_number VARCHAR(30);
ALTER TABLE call_records ADD COLUMN direction VARCHAR(20);
```

### 迁移脚本
自动执行,在 `init_db()` 中调用 `migrate_add_call_record_fields(engine)`

### 示例记录
```
呼入: caller=15012345678, callee=66905712367967212, direction=inbound
呼出: caller=66905712367967212, callee=13912345678, direction=outbound
```

---

## 🎯 下一步行动

1. **立即**: 配置阿里云 CCC 控制台(呼入号码绑定、路由、Webhook)
2. **然后**: 用测试电话拨打 DID 号码,验证完整流程
3. **最后**: 根据测试结果修复问题,优化体验

---

**完成时间**: 2026-09-16 上午  
**代码状态**: ✅ 已修复,已测试(模拟)  
**待办**: ⏳ CCC 控制台配置 + 真实电话测试
