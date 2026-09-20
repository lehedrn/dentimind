# 方案A实施计划：CCC + 阿里云智能语音交互 + 百炼

> 版本：v1.0  
> 日期：2026-09-20  
> 开发周期：15-22天

---

## 一、技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      客户电话                                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              阿里云CCC（云联络中心）                            │
│  - 电话通道（呼入/呼出）                                       │
│  - 呼叫控制                                                   │
│  - 通话录音                                                   │
│  - 音频流转发（WebSocket）                                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ WebSocket (音频流)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              AI对话服务（你的后端，需要开发）                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. ASR服务（阿里云智能语音交互）                      │   │
│  │     - 实时语音识别（流式）                            │   │
│  │     - 返回识别文本                                    │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  2. 对话引擎（你的核心逻辑）                          │   │
│  │     - 接收ASR文本                                    │   │
│  │     - 调用百炼API生成回复                            │   │
│  │     - 管理对话状态和上下文                            │   │
│  │     - 处理业务逻辑（预约、查询等）                    │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  3. TTS服务（阿里云智能语音交互）                      │   │
│  │     - 文本转语音（流式）                              │   │
│  │     - 播放给客户听                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              阿里云百炼（AI对话）                              │
│  - 知识库（口腔FAQ）                                         │
│  - 智能体应用                                                │
│  - Application API                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、开发任务分解

### 阶段1：基础准备（Day 1-2）

#### 1.1 阿里云服务开通
- [ ] 开通阿里云智能语音交互服务
- [ ] 创建语音识别项目（ASR）
- [ ] 创建语音合成项目（TTS）
- [ ] 获取AppKey
- [ ] 了解计费和限制

#### 1.2 技术调研
- [ ] 研究阿里云语音交互SDK
- [ ] 了解实时语音识别API
- [ ] 了解语音合成API
- [ ] 了解CCC音频流转发机制

#### 1.3 开发环境准备
- [ ] 安装语音交互SDK依赖
- [ ] 配置环境变量
- [ ] 创建测试脚本

---

### 阶段2：ASR服务开发（Day 3-6）

#### 2.1 ASR基础集成
- [ ] 创建 `backend/services/asr_service.py`
- [ ] 实现实时语音识别WebSocket客户端
- [ ] 实现音频流接收和发送
- [ ] 实现识别结果回调

#### 2.2 ASR优化
- [ ] 实现中间结果（partial result）处理
- [ ] 实现最终结果（final result）处理
- [ ] 实现语音端点检测（VAD）
- [ ] 添加错误处理和重连机制

#### 2.3 ASR测试
- [ ] 编写ASR测试脚本
- [ ] 测试实时识别准确性
- [ ] 测试延迟和性能

---

### 阶段3：TTS服务开发（Day 7-9）

#### 3.1 TTS基础集成
- [ ] 创建 `backend/services/tts_service.py`
- [ ] 实现语音合成WebSocket客户端
- [ ] 实现文本转语音
- [ ] 实现音频流播放

#### 3.2 TTS优化
- [ ] 实现流式合成（边合成边播放）
- [ ] 实现语音参数调整（语速、音调）
- [ ] 选择合适的语音角色
- [ ] 添加错误处理

#### 3.3 TTS测试
- [ ] 编写TTS测试脚本
- [ ] 测试合成质量
- [ ] 测试延迟

---

### 阶段4：对话引擎开发（Day 10-14）

#### 4.1 对话引擎核心
- [ ] 创建 `backend/services/dialog_engine.py`
- [ ] 实现对话状态管理
- [ ] 实现上下文管理
- [ ] 实现对话流程控制

#### 4.2 集成百炼AI
- [ ] 调用百炼Application API
- [ ] 处理AI回复
- [ ] 管理会话（session_id）

#### 4.3 业务逻辑
- [ ] 实现开场白播放
- [ ] 实现意图识别（咨询、预约、回访）
- [ ] 实现预约信息收集
- [ ] 实现转人工逻辑

#### 4.4 对话引擎测试
- [ ] 编写对话引擎测试
- [ ] 测试多轮对话
- [ ] 测试业务场景

---

### 阶段5：电话控制集成（Day 15-17）

#### 5.1 CCC音频流对接
- [ ] 研究CCC音频流转发机制
- [ ] 实现音频流接收（从CCC）
- [ ] 实现音频流发送（到CCC）
- [ ] 实现通话控制（接听、挂断）

#### 5.2 AI接听实现
- [ ] 配置CCC呼入路由到AI
- [ ] 实现AI自动接听
- [ ] 实现AI对话流程
- [ ] 测试AI接听

#### 5.3 AI外呼实现
- [ ] 实现AI外呼API
- [ ] 实现外呼后AI对话
- [ ] 测试AI外呼

---

### 阶段6：后端API开发（Day 18-19）

#### 6.1 AI电话管理API
- [ ] 创建 `backend/routers/ai_phone.py`
- [ ] 实现AI外呼API
- [ ] 实现AI接听配置API
- [ ] 实现对话记录查询API

#### 6.2 数据库扩展
- [ ] 扩展通话记录表（添加对话内容字段）
- [ ] 创建对话日志表
- [ ] 创建AI配置表

---

### 阶段7：前端开发（Day 20-21）

#### 7.1 AI电话配置页面
- [ ] 创建 `frontend/ai-phone.html`
- [ ] AI外呼界面
- [ ] AI接听配置界面
- [ ] 对话日志查看

#### 7.2 集成到现有系统
- [ ] 添加到导航菜单
- [ ] 集成到客户详情
- [ ] 添加通话记录关联

---

### 阶段8：测试和优化（Day 22）

#### 8.1 端到端测试
- [ ] AI接听完整测试
- [ ] AI外呼完整测试
- [ ] 多轮对话测试
- [ ] 转人工测试

#### 8.2 性能优化
- [ ] 优化延迟（目标<2秒）
- [ ] 优化识别准确率
- [ ] 优化合成质量
- [ ] 添加缓存机制

#### 8.3 错误处理
- [ ] 完善异常处理
- [ ] 添加重试机制
- [ ] 添加降级方案

---

## 三、关键技术点

### 3.1 实时语音识别（ASR）

```python
# 使用阿里云智能语音交互SDK
import nls

class ASRService:
    def __init__(self, appkey, token):
        self.appkey = appkey
        self.token = token
        
    async def start_realtime_recognition(self, audio_stream):
        """
        实时语音识别
        
        Args:
            audio_stream: 音频流（WebSocket）
        
        Returns:
            识别结果生成器
        """
        # 1. 创建 recognizer
        sr = nls.NlsSpeechTranscriber(
            url="wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1",
            token=self.token,
            appkey=self.appkey,
            on_sentence_end=self._on_sentence_end,
            on_start=self._on_start,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        # 2. 开始转录
        sr.start(
            aformat="pcm",
            sample_rate=16000,
            enable_intermediate_result=True,
            enable_punctuation_prediction=True,
            enable_inverse_text_normalization=True
        )
        
        # 3. 发送音频流
        async for audio_chunk in audio_stream:
            sr.send_audio(audio_chunk)
        
        # 4. 停止转录
        sr.stop()
```

### 3.2 语音合成（TTS）

```python
class TTSService:
    def __init__(self, appkey, token):
        self.appkey = appkey
        self.token = token
        
    async def synthesize_speech(self, text, audio_output):
        """
        语音合成
        
        Args:
            text: 要合成的文本
            audio_output: 音频输出流
        """
        # 1. 创建 synthesizer
        tts = nls.NlsSpeechSynthesizer(
            url="wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1",
            token=self.token,
            appkey=self.appkey,
            on_data=self._on_data,
            on_start=self._on_start,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        # 2. 开始合成
        tts.start(
            text=text,
            voice="xiaoyun",  # 语音角色
            aformat="pcm",
            sample_rate=16000,
            volume=50,
            speech_rate=0,
            pitch_rate=0
        )
        
        # 3. 接收音频数据
        async for audio_chunk in audio_output:
            yield audio_chunk
```

### 3.3 对话引擎

```python
class DialogEngine:
    def __init__(self, bailian_service):
        self.bailian = bailian_service
        self.sessions = {}  # 对话会话管理
        
    async def handle_dialog(self, call_id, user_text, audio_stream):
        """
        处理对话
        
        Args:
            call_id: 通话ID
            user_text: 用户说的话（ASR识别结果）
            audio_stream: 音频输出流
        """
        # 1. 获取或创建会话
        session = self.sessions.get(call_id)
        if not session:
            session = await self._create_session(call_id)
            # 播放开场白
            await self._play_greeting(call_id, audio_stream)
        
        # 2. 调用百炼AI生成回复
        ai_reply = await self.bailian.chat(
            session_id=session['session_id'],
            prompt=user_text
        )
        
        # 3. TTS合成语音
        await self.tts.synthesize_speech(ai_reply, audio_stream)
        
        # 4. 保存对话记录
        await self._save_dialog(call_id, user_text, ai_reply)
        
        return ai_reply
```

### 3.4 电话控制

```python
class AIPhoneController:
    async def answer_inbound_call(self, call_id, audio_stream):
        """
        AI接听呼入电话
        
        Args:
            call_id: 通话ID
            audio_stream: 双向音频流
        """
        # 1. 接听电话
        await self.ccc.answer_call(call_id)
        
        # 2. 开始AI对话
        dialog = DialogEngine(self.bailian)
        
        # 3. ASR识别用户说话
        asr = ASRService(self.appkey, self.token)
        async for user_text in asr.start_realtime_recognition(audio_stream):
            # 4. 处理对话
            ai_reply = await dialog.handle_dialog(
                call_id, user_text, audio_stream
            )
            
            # 5. 检查是否需要转人工
            if self._should_transfer_to_human(user_text, ai_reply):
                await self._transfer_to_human(call_id)
                break
        
        # 6. 通话结束
        await self._end_call(call_id)
    
    async def make_ai_outbound_call(self, phone, scenario):
        """
        AI外呼
        
        Args:
            phone: 客户手机号
            scenario: 对话场景
        """
        # 1. 发起外呼
        call_id = await self.ccc.make_call(phone)
        
        # 2. 等待客户接听
        await self._wait_for_answer(call_id)
        
        # 3. 开始AI对话
        await self.answer_inbound_call(call_id, audio_stream)
```

---

## 四、关键依赖

### 4.1 Python依赖

```txt
# requirements.txt
alibabacloud-nls20190228  # 阿里云智能语音交互SDK
websockets                 # WebSocket支持
dashscope                 # 百炼SDK
alibabacloud-ccc20200701  # CCC SDK
```

### 4.2 阿里云服务

| 服务 | 用途 | 费用 |
|------|------|------|
| CCC云联络中心 | 电话通道 | 199元/月/坐席 + 通话费 |
| 智能语音交互（ASR） | 语音识别 | 0.006元/秒 |
| 智能语音交互（TTS） | 语音合成 | 0.002元/100字 |
| 百炼平台 | AI对话 | 按token计费 |

---

## 五、风险和应对

| 风险 | 影响 | 应对方案 |
|------|------|---------|
| CCC音频流转发复杂 | 开发周期延长 | 提前调研，必要时使用CCC内置AI |
| ASR识别不准确 | 用户体验差 | 优化语音参数，添加确认机制 |
| 延迟过高（>3秒） | 用户体验差 | 流式处理，优化网络 |
| 并发能力不足 | 无法同时处理多通电话 | 使用异步架构，水平扩展 |

---

## 六、验收标准

### 6.1 功能验收
- [ ] AI可以自动接听呼入电话
- [ ] AI可以自动外呼并对话
- [ ] 支持多轮对话
- [ ] 支持转人工
- [ ] 对话记录可以保存和查询

### 6.2 性能验收
- [ ] 响应延迟 < 2秒
- [ ] ASR识别准确率 > 90%
- [ ] TTS合成质量清晰
- [ ] 支持至少5通并发电话

### 6.3 稳定性验收
- [ ] 连续运行24小时无故障
- [ ] 异常自动恢复
- [ ] 错误日志完整

---

## 七、下一步行动

### 今天（Day 1）
1. ✅ 开通阿里云智能语音交互服务
2. ✅ 创建ASR和TTS项目
3. ✅ 获取AppKey和Token
4. ✅ 安装SDK依赖
5. ✅ 编写第一个ASR测试脚本

### 本周（Day 1-7）
- [ ] 完成ASR服务开发
- [ ] 完成TTS服务开发
- [ ] 测试ASR和TTS单独工作

### 下周（Day 8-14）
- [ ] 完成对话引擎开发
- [ ] 集成百炼AI
- [ ] 测试对话流程

### 第三周（Day 15-21）
- [ ] 集成CCC电话控制
- [ ] 完成后端API
- [ ] 完成前端界面
- [ ] 端到端测试

---

*文档版本: v1.0*  
*最后更新: 2026-09-20*  
*状态: 开始实施*
