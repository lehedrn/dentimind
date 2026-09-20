# 口腔医院AI客服系统 - 常见问题解答（FAQ）

> 最后更新：2026-09-15  
> 版本：v1.0

---

## 📋 目录

1. [环境配置问题](#1-环境配置问题)
2. [API调用问题](#2-api调用问题)
3. [数据库问题](#3-数据库问题)
4. [CCC外呼问题](#4-ccc外呼问题)
5. [百炼AI问题](#5-百炼ai问题)
6. [前端使用问题](#6-前端使用问题)
7. [系统运维问题](#7-系统运维问题)

---

## 1. 环境配置问题

### Q1.1: 如何配置环境变量？

**A:** 项目使用 `.env` 文件管理环境变量，配置步骤如下：

1. 在项目根目录创建或编辑 `.env` 文件
2. 配置以下必需的环境变量：

```bash
# 阿里云CCC配置
CCC_INSTANCE_ID=your-instance-id
ALIYUN_ACCESS_KEY_ID=your-access-key-id
ALIYUN_ACCESS_KEY_SECRET=your-access-key-secret
CCC_CALLER_NUMBER=your-caller-number
CCC_USER_ID=your-user-id
CCC_DEVICE_ID=your-device-id
CCC_REGION_ID=cn-shanghai

# 百炼AI配置
BAILIAN_APP_ID=your-app-id
DASHSCOPE_API_KEY=your-api-key
BAILIAN_API_ENDPOINT=https://dashscope.aliyuncs.com/api/v1/apps/{app_id}/completion

# 服务配置
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=true

# 数据库配置
DATABASE_URL=sqlite:///./dental_ai.db
```

3. 重启服务使配置生效：
```bash
./service.sh restart
```

### Q1.2: 启动服务时报错"ModuleNotFoundError"怎么办？

**A:** 这是因为Python依赖未安装完整。解决方法：

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装所有依赖
pip install -r requirements.txt

# 验证安装
pip list | grep -E "fastapi|sqlalchemy|dashscope|alibabacloud"
```

如果问题仍然存在，尝试重新创建虚拟环境：

```bash
# 删除旧虚拟环境
rm -rf venv

# 创建新的虚拟环境
python3 -m venv venv

# 激活并安装依赖
source venv/bin/activate
pip install -r requirements.txt
```

### Q1.3: 端口8000被占用怎么办？

**A:** 有两种解决方案：

**方案1：修改服务端口**
```bash
# 编辑 .env 文件
API_PORT=8001  # 改为其他端口

# 重启服务
./service.sh restart
```

**方案2：释放8000端口**
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀掉进程（替换PID）
kill -9 <PID>

# 重启服务
./service.sh restart
```

---

## 2. API调用问题

### Q2.1: API返回404错误怎么办？

**A:** 常见原因和解决方法：

1. **检查API路径是否正确**
   - 正确路径示例：`/api/customers/`、`/api/chat/message`
   - 查看完整API文档：`http://localhost:8000/docs`

2. **检查服务是否运行**
   ```bash
   ./service.sh status
   
   # 如果未运行，启动服务
   ./service.sh start
   ```

3. **检查端口是否正确**
   ```bash
   # 查看当前配置的端口
   grep API_PORT .env
   ```

### Q2.2: API返回500内部错误怎么办？

**A:** 这通常是后端代码错误。排查步骤：

1. **查看错误日志**
   ```bash
   ./service.sh logs
   
   # 或查看最近100行日志
   tail -100 logs/app.log
   ```

2. **常见错误原因**：
   - 数据库连接失败：检查 `DATABASE_URL` 配置
   - CCC API调用失败：检查阿里云配置
   - 百炼API调用失败：检查 `DASHSCOPE_API_KEY` 和 `BAILIAN_APP_ID`

3. **启用调试模式**（仅开发环境）
   ```bash
   # 编辑 .env
   DEBUG=true
   
   # 重启服务
   ./service.sh restart
   ```

### Q2.3: 如何测试API是否正常工作？

**A:** 使用以下命令测试：

```bash
# 1. 健康检查
curl http://localhost:8000/health

# 2. 获取客户列表
curl http://localhost:8000/api/customers/

# 3. 测试聊天API
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session", "message": "你好"}'

# 4. 查看API文档
# 浏览器访问：http://localhost:8000/docs
```

---

## 3. 数据库问题

### Q3.1: 如何初始化数据库？

**A:** 数据库会在首次启动时自动创建。如果需要手动初始化：

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行初始化脚本
python scripts/init_db.py

# 验证数据库
ls -lh dental_ai.db
```

### Q3.2: 如何备份数据库？

**A:** 使用SQLite数据库文件备份：

```bash
# 备份数据库
cp dental_ai.db dental_ai_backup_$(date +%Y%m%d_%H%M%S).db

# 恢复数据库
cp dental_ai_backup_20260915_120000.db dental_ai.db

# 重启服务
./service.sh restart
```

### Q3.3: 如何查看数据库内容？

**A:** 使用SQLite命令行工具：

```bash
# 进入SQLite命令行
sqlite3 dental_ai.db

# 查看所有表
.tables

# 查看客户数据
SELECT * FROM customers LIMIT 10;

# 查看通话记录
SELECT * FROM call_records LIMIT 10;

# 退出
.quit
```

或使用Python脚本：

```bash
python -c "
from backend.models.database import SessionLocal, Customer, CallRecord
db = SessionLocal()
print(f'客户数: {db.query(Customer).count()}')
print(f'通话记录数: {db.query(CallRecord).count()}')
"
```

### Q3.4: 数据库文件在哪里？

**A:** 数据库文件位于项目根目录：

```
/home/workspaces/com/ztq/dentimind/dental_ai.db
```

配置文件中的路径：
```bash
DATABASE_URL=sqlite:///./dental_ai.db
```

---

## 4. CCC外呼问题

### Q4.1: 外呼失败，提示"CallFailed"怎么办？

**A:** 排查步骤：

1. **检查阿里云CCC配置**
   ```bash
   # 验证环境变量
   grep CCC_ .env
   ```

2. **检查网络连接**
   ```bash
   # 测试阿里云API连通性
   curl -I https://ccc.cn-shanghai.aliyuncs.com
   ```

3. **查看错误日志**
   ```bash
   ./service.sh logs | grep -i "ccc\|outbound"
   ```

4. **常见错误原因**：
   - AccessKey权限不足：检查阿里云RAM权限
   - 被叫号码格式错误：使用11位手机号
   - CCC实例未开通：登录阿里云控制台检查

**注意**：当前实现的是**普通电话外呼**功能（非AI对话），客户接听后需要人工客服接听。未来可以升级为AI智能外呼。

### Q4.2: 通话记录没有录音怎么办？

**A:** 录音功能需要正确配置：

1. **检查CCC录音配置**
   - 登录阿里云CCC控制台
   - 确认已开启录音功能
   - 检查录音存储配置

2. **等待录音生成**
   - 录音通常在通话结束后1-2分钟生成
   - 刷新页面查看录音是否出现

3. **检查录音API**
   ```bash
   # 测试录音API
   curl http://localhost:8000/api/ccc/recording/{contact_id}
   ```

### Q4.3: 如何测试外呼功能？

**A:** 使用测试脚本：

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行测试脚本
python scripts/test_call_record_save.py
```

或使用curl命令：

```bash
# 发起外呼
curl -X POST "http://localhost:8000/api/ccc/outbound-call?callee_number=13800138000"

# 查看通话记录
curl "http://localhost:8000/api/ccc/call-records?start_time=1726300800&end_time=1726400800"
```

### Q4.4: 呼入功能如何使用？

**A:** 呼入功能已在代码中实现，但**尚未进行完整测试**。

**已实现的功能**：
- 呼入电话自动识别客户
- 通话记录自动保存
- 通话录音功能
- **人工客服接听**（非AI）

**测试建议**：
1. 配置CCC的呼入号码绑定
2. 使用测试电话呼入
3. 检查通话记录是否正确保存
4. 验证客户自动关联功能
5. **确保有人工客服值守接听**

**注意**：
- 当前呼入电话需要**人工客服接听**
- AI不会自动接听电话
- 如需在生产环境使用，建议先进行完整测试

### Q4.5: AI能自动接听电话吗？

**A:** **不能**。当前系统AI仅处理文字对话，不参与电话语音交流。

**当前电话处理方式**：
- 外呼电话：系统拨号 → 客户接听 → **人工客服**通话
- 呼入电话：客户拨入 → **人工客服**接听

**AI能做的**：
- ✅ 文本客服（24小时自动回复）
- ✅ 通话记录管理
- ✅ 客户数据分析

**AI不能做的**：
- ❌ AI自动外呼并与客户对话
- ❌ AI自动接听呼入电话
- ❌ AI与客户进行语音交流

**未来升级方向**：
- 集成语音识别（ASR）和语音合成（TTS）
- 实现AI电话语音对话
- 支持AI自动外呼和接听
- 需要额外的技术开发投入

**当前建议**：
- 使用文本客服分流咨询
- 电话服务安排人工客服
- 非工作时间引导到文本客服

---

## 5. 百炼AI问题

### Q5.1: AI回复很慢或超时怎么办？

**A:** 可能原因和解决方法：

1. **检查网络连接**
   ```bash
   # 测试百炼API连通性
   curl -I https://dashscope.aliyuncs.com
   ```

2. **检查API配额**
   - 登录阿里云百炼控制台
   - 查看API调用配额和余额
   - 必要时申请提升配额

3. **优化提示词**
   - 减少提示词长度
   - 避免复杂的上下文

4. **设置超时时间**
   ```python
   # 在 bailian_chat.py 中调整超时
   response = requests.post(url, json=data, timeout=30)
   ```

### Q5.2: AI回复内容不准确怎么办？

**A:** 优化知识库和提示词：

1. **更新知识库**
   ```bash
   # 编辑知识库文档
   vim docs/knowledge/dental-faq-knowledge-base.md
   
   # 添加更多专业内容
   # 例如：常见口腔问题、治疗方案、价格等
   ```

2. **调整系统提示词**
   ```python
   # 在 bailian_chat.py 中修改系统提示词
   system_prompt = """
   你是口腔医院的专业AI客服小雅...
   请根据知识库内容回答用户问题...
   """
   ```

3. **测试回复质量**
   ```bash
   # 使用测试脚本
   python scripts/test_bailian.py
   ```

### Q5.3: 如何实现多轮对话？

**A:** 系统已支持多轮对话，使用 `session_id`：

```javascript
// 前端代码示例
let sessionId = 'session-' + Date.now();

// 第一次对话
const response1 = await fetch('/api/chat/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        session_id: sessionId,
        message: '我想咨询种植牙'
    })
});

// 后续对话使用相同的 session_id
const response2 = await fetch('/api/chat/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        session_id: sessionId,  // 使用相同的session_id
        message: '多少钱？'
    })
});
```

### Q5.4: API Key泄露了怎么办？

**A:** 立即采取以下措施：

1. **禁用泄露的API Key**
   - 登录阿里云控制台
   - 找到对应的AccessKey
   - 禁用或删除该Key

2. **生成新的API Key**
   - 在阿里云控制台创建新的AccessKey
   - 更新 `.env` 文件中的配置

3. **重启服务**
   ```bash
   ./service.sh restart
   ```

4. **检查安全配置**
   - 确保 `.env` 文件不提交到Git
   - 检查 `.gitignore` 配置

---

## 6. 前端使用问题

### Q6.1: 页面加载很慢怎么办？

**A:** 优化建议：

1. **检查网络速度**
   - 使用浏览器开发者工具（F12）查看网络面板
   - 检查是否有大文件加载缓慢

2. **启用浏览器缓存**
   - 静态资源已配置缓存策略
   - 清除浏览器缓存后重试

3. **检查后端性能**
   ```bash
   # 查看API响应时间
   ./service.sh logs | grep "HTTP"
   ```

### Q6.2: 聊天界面不显示消息怎么办？

**A:** 排查步骤：

1. **打开浏览器开发者工具**（F12）
   - 查看Console面板是否有错误
   - 查看Network面板检查API调用

2. **检查后端服务**
   ```bash
   ./service.sh status
   ./service.sh logs | grep chat
   ```

3. **测试API**
   ```bash
   curl -X POST http://localhost:8000/api/chat/message \
     -H "Content-Type: application/json" \
     -d '{"session_id": "test", "message": "你好"}'
   ```

### Q6.3: 如何自定义前端样式？

**A:** 修改CSS样式：

1. **找到样式定义位置**
   ```bash
   # 编辑对应HTML文件
   vim frontend/customers.html
   vim frontend/outbound.html
   vim frontend/chat-widget.html
   ```

2. **修改CSS样式**
   ```html
   <style>
   /* 修改主题颜色 */
   .header {
       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
   }
   
   /* 修改按钮样式 */
   .add-btn {
       background: #your-color;
   }
   </style>
   ```

3. **刷新页面查看效果**
   - 硬刷新：Ctrl+F5（Windows）或 Cmd+Shift+R（Mac）

---

## 7. 系统运维问题

### Q7.1: 如何查看系统日志？

**A:** 使用以下方式查看日志：

```bash
# 1. 使用服务脚本
./service.sh logs

# 2. 查看实时日志
tail -f logs/app.log

# 3. 查看最近100行
tail -100 logs/app.log

# 4. 搜索错误日志
grep -i "error\|exception" logs/app.log
```

### Q7.2: 如何重启服务？

**A:** 使用服务管理脚本：

```bash
# 重启服务
./service.sh restart

# 或手动重启
./service.sh stop
./service.sh start

# 查看状态
./service.sh status
```

### Q7.3: 如何更新代码？

**A:** 更新步骤：

```bash
# 1. 停止服务
./service.sh stop

# 2. 备份数据库
cp dental_ai.db dental_ai_backup_$(date +%Y%m%d_%H%M%S).db

# 3. 更新代码（如果使用Git）
git pull origin main

# 4. 安装新依赖（如果有）
source venv/bin/activate
pip install -r requirements.txt

# 5. 启动服务
./service.sh start

# 6. 验证服务
curl http://localhost:8000/health
```

### Q7.4: 如何监控系统运行状态？

**A:** 使用以下方式监控：

```bash
# 1. 查看服务状态
./service.sh status

# 2. 查看进程信息
ps aux | grep uvicorn

# 3. 查看端口占用
lsof -i :8000

# 4. 查看系统资源
top -p $(pgrep -f uvicorn)

# 5. 查看数据库大小
ls -lh dental_ai.db
```

### Q7.5: 如何部署到生产环境？

**A:** 生产环境部署建议：

1. **关闭调试模式**
   ```bash
   # 编辑 .env
   DEBUG=false
   ```

2. **使用生产级WSGI服务器**
   ```bash
   # 安装gunicorn
   pip install gunicorn
   
   # 使用gunicorn启动
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:8000
   ```

3. **配置HTTPS**
   - 使用Nginx反向代理
   - 配置SSL证书

4. **配置日志轮转**
   ```bash
   # 使用logrotate管理日志
   /etc/logrotate.d/dental-ai
   ```

5. **定期备份数据库**
   ```bash
   # 添加crontab定时任务
   0 2 * * * cp /path/to/dental_ai.db /backup/dental_ai_$(date +\%Y\%m\%d).db
   ```

---

## 📞 技术支持

如果以上FAQ未能解决您的问题，请：

1. **查看项目文档**
   - README.md - 项目概览
   - docs/manual-test-guide.md - 操作手册
   - docs/quick-test-guide.md - 快速测试指南

2. **检查日志**
   ```bash
   ./service.sh logs
   ```

3. **联系技术支持**
   - 提交Issue到项目仓库
   - 联系系统管理员

---

## 📝 更新记录

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-09-15 | v1.0 | 初始版本，包含7大类常见问题 |

---

*文档维护：口腔医院AI客服系统开发团队*  
*联系方式：support@dental-ai.com*
