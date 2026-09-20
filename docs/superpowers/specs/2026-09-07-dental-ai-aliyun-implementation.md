# 口腔医院AI客服系统 — 完整技术方案（阿里云语音服务版）

> 日期：2026-09-07
> 状态：实施中
> 技术栈：Dify + LiveKit + 阿里云语音服务

---

## 一、方案概述

### 1.1 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户触点层                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │
│  │ 网页聊天    │  │ AI外呼      │  │  AI接听            │ │
│  │ (文本客服)  │  │ (主动拨打)  │  │  (来电应答)        │ │
│  └─────┬──────┘  └─────┬──────┘  └──────────┬─────────┘ │
└────────┼───────────────┼────────────────────┼───────────┘
         │               │                    │
         ▼               ▼                    ▼
┌─────────────────────────────────────────────────────────┐
│                    对话引擎层                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Dify (LLMOps平台)                    │  │
│  │  - 知识库管理（口腔FAQ）                           │  │
│  │  - 对话流程编排                                    │  │
│  │  - LLM对话生成（DeepSeek/通义千问）                │  │
│  │  - 文本通道直接响应                                │  │
│  │  - API供语音通道调用                               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         ▲                       │
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────────────────────┐
│                    语音处理层                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │            LiveKit Agents (语音AI框架)             │  │
│  │  - ASR语音识别（阿里云智能语音）                    │  │
│  │  - TTS语音合成（阿里云智能语音）                    │  │
│  │  - 通话状态管理                                    │  │
│  │  - 调用Dify API获取AI回复                          │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         ▲                       │
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────────────────────┐
│                    通信基础设施层                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │          阿里云语音服务 (SIP Trunk)                │  │
│  │  - SIP协议对接                                    │  │
│  │  - PSTN电话网连接                                 │  │
│  │  - 外呼/接听电话                                  │  │
│  │  - 录音、通话记录                                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 1.2 三个场景的数据流

#### 场景1：文本客服

```
用户打字 → 网页聊天窗口 → Dify直接处理 → 知识库检索 + LLM生成 → 文字回复
```

#### 场景2：AI外呼

```
系统发起外呼请求
    ↓
LiveKit通过阿里云SIP Trunk拨打手机号
    ↓
对方接听
    ↓
用户说话 → 阿里云ASR转文字 → LiveKit调用Dify API → 获取AI回复
    ↓
阿里云TTS合成语音 → 播放给用户 → 循环
    ↓
通话结束 → 结果回调
```

#### 场景3：AI接听

```
用户拨打指定号码
    ↓
阿里云语音服务接收来电 → Webhook通知
    ↓
LiveKit接听 → 建立通话
    ↓
用户说话 → 阿里云ASR转文字 → LiveKit调用Dify API → 获取AI回复
    ↓
阿里云TTS合成语音 → 播放给用户 → 循环
    ↓
通话结束 → 结果回调
```

---

## 二、阿里云语音服务对接

### 2.1 申请流程

**前提条件**：需要企业实名认证（口腔医院可以）

**步骤**：

1. **注册阿里云账号**
   - 访问 https://account.aliyun.com
   - 使用医院营业执照做企业实名认证

2. **开通语音服务**
   - 访问 https://vms.console.aliyun.com
   - 开通"语音服务"
   - 完成语音服务资质审核（提供话术脚本）

3. **购买号码**
   - 在控制台购买语音号码
   - 费用：35元/月（基础号）
   - 选择归属地（建议选择医院所在地）

4. **获取SIP Trunk信息**
   - 在控制台创建SIP Trunk
   - 获取：SIP服务器地址、账号、密码

### 2.2 阿里云语音服务API

**核心API**：

```python
from aliyunsdkcore.client import AcsClient
from aliyunsdkvms.request.v20170525 import (
    SingleCallByTtsRequest,      # 文本转语音外呼
    SmartCallRequest,            # 智能外呼
    ClickToDialRequest,          # 点击拨号
)

# 初始化客户端
client = AcsClient(
    "<your-access-key-id>",
    "<your-access-key-secret>",
    "cn-hangzhou"
)

# 示例：智能外呼（AI机器人）
request = SmartCallRequest.SmartCallRequest()
request.set_CalledNumber("13800138000")           # 对方手机号
request.set_CalledShowNumber("01012345678")       # 显示的号码（阿里云分配的）
request.set_TtsParam("{'customer_name':'张先生'}") # 模板变量
request.set_OutId("call-12345")                   # 外部ID

response = client.do_action_with_exception(request)
```

### 2.3 SIP Trunk对接LiveKit

**LiveKit配置**：

```yaml
# livekit-server.yaml
sip:
  enabled: true
  trunks:
    - name: aliyun-voice-service
      # 阿里云SIP服务器地址
      address: sip-vms.aliyuncs.com
      # SIP认证信息（从阿里云控制台获取）
      username: your_aliyun_sip_username
      password: your_aliyun_sip_password
      # 分配的号码
      numbers: ["+861012345678"]
      # 传输协议
      transport: udp
      # 可选：TLS加密
      # transport: tls
      # 可选：SRTP加密
      # rtp_encryption: true
```

### 2.4 发起外呼

```python
from livekit import api
import asyncio

async def make_outbound_call(phone_number: str, customer_name: str):
    """
    通过阿里云语音服务发起外呼
    """
    sip_client = api.SipClient()
    
    # 创建SIP参与者（触发外呼）
    response = await sip_client.create_sip_participant(
        sip_trunk_id="aliyun-voice-service",
        call_to=f"sip:{phone_number}",
        room_name=f"dental-call-{phone_number}-{int(asyncio.get_event_loop().time())}",
        participant_identity="ai-customer-service",
        participant_name="口腔医院AI客服",
        headers={
            "X-Customer-Name": customer_name,
            "X-Call-Type": "outbound",
        }
    )
    
    return response.sip_call_id

# 使用示例
asyncio.run(make_outbound_call("13800138000", "张先生"))
```

### 2.5 接听来电

**阿里云配置来电Webhook**：

在阿里云控制台配置：
- 来电号码：01012345678
- Webhook URL：https://your-server.com/webhook/incoming-call

**处理来电Webhook**：

```python
from flask import Flask, request, jsonify
from livekit import api

app = Flask(__name__)

@app.route("/webhook/incoming-call", methods=["POST"])
def handle_incoming_call():
    """
    处理阿里云来电Webhook
    """
    data = request.json
    caller_number = data.get("From")        # 来电号码
    called_number = data.get("To")          # 被叫号码（你的号码）
    call_id = data.get("CallId")            # 通话ID
    
    # 创建LiveKit房间，让AI Agent加入
    room_name = f"incoming-{caller_number}-{int(time.time())}"
    
    # 将SIP通话桥接到LiveKit房间
    sip_client = api.SipClient()
    await sip_client.create_sip_participant(
        sip_trunk_id="aliyun-voice-service",
        call_to=f"sip:{caller_number}",
        room_name=room_name,
        participant_identity="ai-customer-service",
        participant_name="口腔医院AI客服",
    )
    
    # 返回TWIML响应（告诉阿里云如何处理通话）
    return jsonify({
        "response": {
            "dial": {
                "sip": f"sip:{room_name}@livekit-server:7880"
            }
        }
    })
```

---

## 三、LiveKit Agent实现

### 3.1 Agent核心代码

```python
from livekit import agents, rtc
from livekit.plugins import aliyun, deepgram, openai, silero
import requests
import os

async def entrypoint(ctx: agents.JobContext):
    """
    AI客服Agent入口
    """
    await ctx.connect()
    
    # 从房间属性获取客户信息
    customer_name = ctx.room.name.split("-")[1] if "-" in ctx.room.name else "客户"
    
    # 创建语音处理管道
    pipeline = agents.voice.VoicePipeline(
        # 语音识别：阿里云智能语音（中文优化）
        stt=aliyun.STT(
            app_key=os.getenv("ALIYUN_ASR_APP_KEY"),
            language="zh-CN",
        ),
        # LLM：调用Dify API
        llm=DifyAgent(customer_name=customer_name),
        # 语音合成：阿里云智能语音
        tts=aliyun.TTS(
            app_key=os.getenv("ALIYUN_TTS_APP_KEY"),
            voice="xiaoyun",  # 女声，温和
        ),
        # 语音活动检测
        vad=silero.VAD.load(),
    )
    
    # 开始处理
    await pipeline.start(ctx.room)
    
    # 开场白
    await pipeline.say("您好，这里是XX口腔医院，请问有什么可以帮您？")


class DifyAgent(agents.llm.LLM):
    """
    调用Dify API的LLM实现
    """
    def __init__(self, customer_name: str):
        self.customer_name = customer_name
        self.dify_api_key = os.getenv("DIFY_API_KEY")
        self.dify_base_url = os.getenv("DIFY_BASE_URL", "http://localhost/v1")
    
    async def chat(self, messages: list[agents.llm.ChatMessage]) -> str:
        """
        调用Dify的/chat-messages接口
        """
        # 获取用户最新输入
        user_message = messages[-1].text if messages else ""
        
        # 调用Dify API
        response = requests.post(
            f"{self.dify_base_url}/chat-messages",
            headers={
                "Authorization": f"Bearer {self.dify_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "inputs": {
                    "customer_name": self.customer_name,
                },
                "query": user_message,
                "response_mode": "blocking",
                "conversation_id": "",  # 空字符串表示新对话
                "user": f"phone-{self.customer_name}",
            },
            timeout=30,
        )
        
        result = response.json()
        return result.get("answer", "抱歉，我没有听清，您能再说一遍吗？")


if __name__ == "__main__":
    # 启动Agent
    agents.run_app(entrypoint())
```

### 3.2 环境变量配置

```bash
# .env文件
# 阿里云语音服务
ALIYUN_ASR_APP_KEY=your_asr_app_key
ALIYUN_TTS_APP_KEY=your_tts_app_key
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret

# Dify
DIFY_API_KEY=your_dify_api_key
DIFY_BASE_URL=http://localhost/v1

# LiveKit
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

---

## 四、Dify知识库配置

### 4.1 口腔FAQ知识库内容

**准备50-80条FAQ，覆盖以下类别**：

#### 基础服务类（20条）

```markdown
Q: 你们医院在哪里？有几家门店？
A: 我们是XX口腔医院连锁，在本市有80多家门店，覆盖各个区域。请问您住在哪个区？我可以为您推荐最近的门店。

Q: 你们营业时间是什么？
A: 我们的营业时间是每天早上8:30到晚上18:00，周末和节假日正常营业。建议您提前预约，可以避免排队。

Q: 怎么预约？
A: 您可以通过以下方式预约：1）直接回复您的姓名、电话和想预约的时间；2）拨打我们的客服热线；3）通过我们的小程序预约。请问您需要预约什么项目？

Q: 洗牙多少钱？
A: 我们的洗牙项目价格是198元，包含超声波洁牙、抛光和口腔检查。现在有新客户优惠，首次洗牙只要98元。您需要预约吗？

Q: 洗牙疼不疼？
A: 洗牙过程基本不疼，只会有轻微的酸胀感。我们的医生都很专业，会尽量让您舒适。如果您的牙齿比较敏感，我们可以使用表面麻醉膏。请问您之前洗过牙吗？

Q: 种植牙多少钱？
A: 种植牙的价格根据品牌不同有所差异：韩国登腾种植牙5800元/颗，瑞士ITI种植牙9800元/颗，瑞典诺贝尔种植牙12800元/颗。这个价格包含种植体、基台和牙冠。您需要我介绍详细流程吗？

Q: 种植牙需要多长时间？
A: 种植牙整个流程大概需要3-6个月：1）第一次就诊：口腔检查、CT拍片、制定方案（1小时）；2）植入种植体（30分钟）；3）等待3-6个月骨结合；4）安装基台和牙冠（2次就诊）。请问您的牙齿是什么情况？

Q: 儿童补牙多少钱？
A: 儿童补牙价格是280元/颗，使用的是进口树脂材料，安全无毒。如果龋齿比较严重，可能需要做预成冠，价格是680元/颗。建议尽早补牙，避免龋齿加重。请问孩子几岁了？

Q: 牙齿矫正多少钱？
A: 牙齿矫正的价格根据矫正器类型不同：金属托槽矫正12000元起，陶瓷半隐形矫正18000元起，隐形矫正（隐适美）28000元起。具体价格需要根据您的牙齿情况评估。建议您来做个免费的口腔检查，医生会给您详细方案。

Q: 拔智齿多少钱？
A: 拔智齿的价格根据难度不同：简单拔除300元/颗，复杂拔除（阻生齿）800-1500元/颗。价格包含麻醉费、手术费和术后消炎药。请问您的智齿是什么情况？有拍过片吗？
```

#### 预约流程类（10条）

```markdown
Q: 预约需要哪些信息？
A: 预约需要提供：1）您的姓名；2）联系电话；3）想预约的项目（如洗牙、补牙等）；4）希望的时间和门店。我会帮您安排。

Q: 可以当天预约当天看吗？
A: 可以的，如果当天还有号源，可以当天预约。但建议您提前1-2天预约，可以选择更合适的时间段。请问您想预约什么时候？

Q: 预约后可以取消或改期吗？
A: 可以的，您可以在就诊前2小时联系我们取消或改期，不收取任何费用。建议您如果需要改期尽早告知，方便我们安排其他患者。

Q: 预约后需要带什么？
A: 请您带上：1）身份证；2）医保卡（如果有）；3）之前的病历或X光片（如果有）。建议提前15分钟到达，填写就诊登记表。
```

#### 其他常见问题（20条）

```markdown
Q: 你们可以用医保吗？
A: 我们是医保定点单位，可以使用医保卡。但需要注意，医保只能报销部分项目（如拔牙、补牙、根管治疗等），美容类项目（如洗牙、矫正、种植牙）需要自费。请问您想做什么项目？

Q: 你们晚上开门吗？
A: 我们部分门店有夜间门诊，营业时间到晚上20:00。请问您在哪个区？我帮您查一下附近有夜间门诊的门店。

Q: 你们有停车场吗？
A: 大部分门店都有停车场或周边有停车场。请问您预约哪家门店？我可以告诉您具体的停车位置。

Q: 看牙疼不疼？你们有无痛治疗吗？
A: 我们有无痛治疗技术，使用进口麻醉药，治疗过程基本无痛。如果比较紧张，还可以选择笑气镇静或静脉镇静。请问您是什么项目？我帮您安排经验丰富的医生。

Q: 你们医院正规吗？医生资质怎么样？
A: 我们是正规口腔医院连锁，所有医生都有执业医师资格证，平均临床经验10年以上。我们的医疗机构执业许可证可以在卫健委官网查询。请问您想了解哪家门店的医生？
```

### 4.2 Dify配置

**步骤**：

1. **创建知识库**
   - 名称：口腔医院FAQ
   - 上传上述FAQ文档（支持Markdown、TXT、PDF）
   - 分段设置：按Q&A分段

2. **创建聊天应用**
   - 名称：口腔医院AI客服
   - 关联知识库：口腔医院FAQ
   - LLM选择：DeepSeek（便宜好用）或通义千问

3. **配置System Prompt**

```markdown
你是XX口腔医院的AI客服助手，名叫小雅。你的任务是：

1. 热情、专业地回答患者的口腔健康问题
2. 介绍医院的服务项目、价格、流程
3. 帮助患者预约就诊
4. 必要时引导患者到院就诊

注意事项：
- 语气要温和、耐心，像专业的医疗顾问
- 如果患者的问题超出知识库范围，诚实说明并建议咨询医生
- 涉及价格时，要说明"具体价格需要医生评估后确定"
- 如果患者想预约，收集：姓名、电话、项目、时间、门店偏好
- 不要给出具体的医疗诊断，只给一般性建议

开场白：
"您好，这里是XX口腔医院，我是AI客服小雅。请问有什么可以帮您？"
```

4. **获取API Key**
   - 在应用设置中获取API Key
   - 用于LiveKit Agent调用

---

## 五、部署架构

### 5.1 服务器配置

**最小配置（演示阶段）**：

```yaml
# 单台服务器
CPU: 4核
内存: 8GB
硬盘: 100GB SSD
带宽: 5Mbps
系统: Ubuntu 22.04

# 运行服务：
# - Dify (Docker)
# - LiveKit Server (Docker)
# - LiveKit Agent (Python)
# - Nginx (反向代理)
```

**推荐配置（生产阶段）**：

```yaml
# 应用服务器
CPU: 8核
内存: 16GB
硬盘: 200GB SSD
带宽: 10Mbps

# 数据库服务器（可选，Dify可以外接数据库）
CPU: 4核
内存: 8GB
硬盘: 500GB SSD
```

### 5.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Dify
  dify-api:
    image: langgenius/dify-api:latest
    environment:
      - MODE=api
      - SECRET_KEY=your_secret_key
      - DB_HOST=dify-db
      - REDIS_HOST=dify-redis
    depends_on:
      - dify-db
      - dify-redis
  
  dify-web:
    image: langgenius/dify-web:latest
    ports:
      - "3000:3000"
  
  dify-db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=your_password
    volumes:
      - dify-db-data:/var/lib/postgresql/data
  
  dify-redis:
    image: redis:7
    volumes:
      - dify-redis-data:/data
  
  # LiveKit Server
  livekit:
    image: livekit/livekit-server:latest
    command: --config /etc/livekit.yaml
    ports:
      - "7880:7880"   # WebSocket
      - "7881:7881"   # HTTP
      - "7882:7882/udp"  # TURN
      - "3478:3478/udp"  # TURN
    volumes:
      - ./livekit-server.yaml:/etc/livekit.yaml
  
  # LiveKit Agent
  livekit-agent:
    build: ./livekit-agent
    environment:
      - LIVEKIT_URL=ws://livekit:7880
      - LIVEKIT_API_KEY=your_api_key
      - LIVEKIT_API_SECRET=your_api_secret
      - DIFY_API_KEY=your_dify_key
      - ALIYUN_ASR_APP_KEY=your_asr_key
      - ALIYUN_TTS_APP_KEY=your_tts_key
    depends_on:
      - livekit

volumes:
  dify-db-data:
  dify-redis-data:
```

---

## 六、成本估算

### 6.1 阿里云语音服务费用

| 项目 | 单价 | 月费用（100通/天） |
|---|---|---|
| 号码月租 | 35元/月 | 35元 |
| 通话费 | 0.11元/分钟 | 0.11 × 5分钟 × 100通 × 30天 = 1650元 |
| ASR语音识别 | 0.15元/分钟 | 0.15 × 5分钟 × 100通 × 30天 = 2250元 |
| TTS语音合成 | 包含在通话费中 | 0元 |
| **小计** | | **3935元/月** |

### 6.2 LLM费用

| 模型 | 单价 | 月费用估算 |
|---|---|---|
| DeepSeek | 输入0.14元/百万token，输出0.28元/百万token | 约200元/月 |
| 通义千问 | 输入0.008元/千token，输出0.02元/千token | 约300元/月 |

### 6.3 服务器费用

| 配置 | 月费用 |
|---|---|
| 阿里云ECS 4核8G | 约300元/月 |
| 阿里云ECS 8核16G | 约600元/月 |

### 6.4 总成本

**演示阶段（通话量少）**：
- 阿里云语音服务：200元/月（按量计费）
- LLM：100元/月
- 服务器：300元/月
- **总计：约600元/月**

**生产阶段（100通/天）**：
- 阿里云语音服务：3935元/月
- LLM：300元/月
- 服务器：600元/月
- **总计：约4835元/月**

---

## 七、实施计划

### 7.1 时间线（4周）

#### Week 1：基础设施 + 文本客服

| Day | 任务 | 交付物 |
|---|---|---|
| 1-2 | 购买服务器，部署Docker环境 | 服务器就绪 |
| 3-4 | 部署Dify，准备口腔FAQ知识库 | Dify可访问 |
| 5-6 | 配置对话流程，调试Prompt | 文本客服可用 |
| 7 | 生成网页聊天窗口 | **里程碑1：文本客服Demo** |

#### Week 2：语音通道

| Day | 任务 | 交付物 |
|---|---|---|
| 8-9 | 部署LiveKit Server | LiveKit就绪 |
| 10-11 | 开发LiveKit Agent，对接Dify API | Agent可运行 |
| 12-13 | 对接阿里云ASR/TTS | 语音识别/合成可用 |
| 14 | 端到端联调（浏览器语音通话） | **里程碑2：语音Demo** |

#### Week 3：阿里云语音服务对接

| Day | 任务 | 交付物 |
|---|---|---|
| 15-16 | 客户申请阿里云语音服务，完成认证 | 拿到SIP Trunk信息 |
| 17-18 | 配置LiveKit SIP Trunk | SIP对接完成 |
| 19-20 | 实现外呼功能 | 可以拨打真实电话 |
| 21 | 实现接听功能 | 可以接听来电 |
| | | **里程碑3：真实电话可用** |

#### Week 4：演示准备

| Day | 任务 | 交付物 |
|---|---|---|
| 22-23 | 编写演示话术脚本 | 3-5个演示场景 |
| 24-25 | 全流程联调，优化体验 | 系统稳定 |
| 26-27 | 准备演示材料（PPT、备份方案） | 演示材料齐全 |
| 28 | 内部演练2-3遍 | **里程碑4：可以面对客户演示** |

### 7.2 关键里程碑

1. **Day 7**：文本客服Demo可演示
2. **Day 14**：语音AI对话可演示（浏览器）
3. **Day 21**：真实电话外呼/接听可用
4. **Day 28**：完整的演示系统就绪

---

## 八、风险与备选方案

| 风险 | 影响 | 备选方案 |
|---|---|---|
| 阿里云语音服务审批延迟 | 无法对接真实电话 | 先用浏览器语音Demo，说明正式部署后接入电话 |
| ASR/TTS中文效果不好 | 语音识别准确率低 | 切换到讯飞ASR/TTS（需额外费用） |
| Dify知识库检索不准 | AI回答不准确 | 优化知识库分段，调整检索策略 |
| 服务器性能不足 | 系统卡顿 | 升级服务器配置，或分离部署 |

---

## 九、后续扩展

合同签署后，可以扩展的功能：

1. **企业微信集成**：将AI客服接入企业微信，自动回复客户咨询
2. **私域SOP**：自动发送预约提醒、术后回访等
3. **多门店管理**：每个门店独立的知识库和统计数据
4. **数据分析**：通话记录、客户画像、转化率分析
5. **CRM集成**：对接医院的客户管理系统

---

## 附录：需要准备的账号和资源

### 阿里云账号

- [ ] 阿里云主账号（企业实名认证）
- [ ] 开通语音服务
- [ ] 购买语音号码
- [ ] 开通智能语音交互（ASR/TTS）
- [ ] 获取AccessKey ID和Secret

### Dify账号

- [ ] 部署Dify
- [ ] 创建聊天应用
- [ ] 创建知识库，上传FAQ
- [ ] 获取API Key

### LiveKit账号

- [ ] 部署LiveKit Server
- [ ] 配置API Key和Secret
- [ ] 配置SIP Trunk（阿里云）

### 其他

- [ ] 服务器（阿里云ECS或自建）
- [ ] 域名（可选，用于Webhook）
- [ ] SSL证书（可选，用于HTTPS）

---

**文档版本**：v1.0
**最后更新**：2026-09-07
**状态**：待实施
