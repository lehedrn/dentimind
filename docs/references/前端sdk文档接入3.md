通过该文档，您可以将坐席工作台嵌入到第三方系统中，直接在您的系统中实现单点登录、接打电话等功能，并且您可以通过监听SDK中的方法来实现来电弹屏。下面的工作需要您公司的前端工程师来实施。您可以随时关注该文档页面，SDK有更新时会及时更新文档页面。

## 前端资源

**重要**

**更新前端资源版本以后，一定要在本地环境做全面测试以后再发布线上环境！**

### **UI版本**

```
<!-- IM sdk样式文件，不使用IM插件不要加载此文件-->
<link rel="stylesheet" type="text/css" href="//g.alicdn.com/code/npm/@ali/cc-im-sdk/{version-im-sdk}/index.css">
<!-- 软电话sdk样式文件-PC端（使用IM插件也得加载） -->
<link rel="stylesheet" type="text/css" href="//g.alicdn.com/cloudcallcenter/web-workbench-sdk/{version-workbench}/ui.min.css">
<!-- 软电话sdk样式文件-移动端（二选一即可，不可两个都加载）-->
<link rel="stylesheet" type="text/css" href="//g.alicdn.com/cloudcallcenter/web-workbench-sdk/{version-workbench}/ui-mobile.min.css">

<!-- IM sdk js文件，不使用IM插件不要加载此文件-->
<script src="//g.alicdn.com/code/npm/@ali/cc-im-sdk/{version-im-sdk}/index.js"></script>
<!-- 软电话sdk js文件（使用IM插件也得加载） -->
<script src="//g.alicdn.com/cloudcallcenter/web-workbench-sdk/{version-workbench}/ui.min.js"></script>
```

### **核心版本**

```
<!-- 软电话sdk js文件-->
<script src="//g.alicdn.com/cloudcallcenter/web-workbench-sdk/{version-workbench}/core.min.js"></script>
```

**重要**

-   **UI版本脚本资源请放在</body>标签之前，请勿放在head标签中，因为脚本加载后会对document.body做操作。**
    
-   **以上静态资源，把上面的{version-im-sdk}和{version-workbench}替换为对应的版本号，当前最新版本号为：**
    
    **version-im-sdk ==> 1.8.1**
    
    **version-workbench ==> 3.8.1**
    

**注意：要使用IMSDK插件，请使用UI版本，且cc-im-sdk和web-workbench-sdk需要按照上述顺序都加载。**

### **UI版本和核心版本的区别**

UI版本（ui.min.js）：有界面操作，有核心逻辑，需要加载CSS和JS资源。

核心版本（core.min.js）：没有界面，但是有核心逻辑，适合自定义UI界面的业务方，只需要加载一个JS资源。

**重要**

两个版本的JS资源**不可同时**加载，会造成`window.CCCWorkbenchSDK`全局变量被后一个加载的覆盖，造成不符合预期的问题。

## 初始化SDK

接入SDK之前需要完成以下工作：

1.  建议使用Chrome浏览器，版本号为72及以上，优先使用最新版本。
    
2.  SDK所嵌入的自有业务系统**必须使用HTTPS协议**。原因是Chrome在47版本之后，禁止HTTP协议获取系统麦克风权限，这会造成无法正常通话。
    
3.  如果您是在iframe标签内使用SDK，那么需要为iframe标签增加allow="microphone; camera; autoplay"属性，来允许iframe标签获取系统麦克风、摄像头权限和音视频自动播放权限。
    

初始化SDK：

```
if (window.workbench) {
  // 不重复初始化
  return;
}
window.workbench = new window.CCCWorkbenchSDK({
  dom: 'workbench-container', // UI版本必填，且在 id为workbench-container的dom加载完成后初始化
  instanceId: 'xxxxxx', // 填写真实的实例ID
  exportErrorOfApi: true,
  afterCallRule: 15, // 话后处理时长
  ajaxPath: '/api', // 根据后端接口地址更改
  logger: {
    builtinEnabled: false,
  },
  imConfig: {
    getContainer() {
      return document.getElementById('im-container');
    },
  },
  onInit() {
    console.log('onInit');
    // window.workbench.register() // 初始化好后，自动注册上线
  },
  onRegister(event) {
    console.log('onRegister', event);
  },
  onLogIn(event) {
    console.log('onLogIn', event);
  },
  onBreak(event) {
    console.log('onBreak', event);
  },
  onChangeInvisibility(event) {
    console.log('onChangeInvisibility', event);
  },
  onReady() {
    console.log('onReady');
  },
  onCallComing(event) {
    console.log('onCallComing', event);
  },
  onCallDialing(event) {
    console.log('onCallDialing', event);
  },
  onCallEstablish(event) {
    console.log('onCallEstablish', event);
  },
  onCallRelease(event) {
    console.log('onCallRelease', event);
  },
  onDeviceTypeChange(event) {
    console.log('onDeviceTypeChange', event);
  },
  onErrorNotify(event) {
    console.log('onErrorNotify', event);
  },
  onHangUp(event) {
    console.log('onHangUp', event);
  },
  onLogOut() {
    console.log('onLogOut');
  },
  onSelectOutboundNumber(event) {
    console.log('onSelectOutboundNumber', event);
  },
  onStatusChange(event) {
    console.log('onStatusChange', event);
  },
  onWorkModeChange(event) {
    console.log('onWorkModeChange', event);
  },
  onBeforeCallDialing(payload) {
    console.log('onBeforeCallDialing', payload);
    payload.callback(); // 必须调用
  },
  onBeforeCallHangup(payload) {
    console.log('onBeforeCallHangup', payload);
    payload.callback();
  },
  onAgentStats(event) {
    console.log('onAgentStats', event);
  },
  onSelectCurrentCallRecord(event) {
    console.log('onSelectCurrentCallRecord', event);
  },
  onAfterEarlyMediaRecognized(event) {
    console.log('onAfterEarlyMediaRecognized', event);
  },
  onSignedSkillGroupChange(signedSkillGroupList) {
    console.log('onSignedSkillGroupChange', signedSkillGroupList);
  },
  onBeingMonitored(event) {
    console.log('onBeingMonitored', event);
  },
  onIvrTrackingAISummary(event) {
    console.log('onIvrTrackingAISummary', event);
  },
});
```

## config必选配置

| **参数** | **描述** | **类型** |
| --- | --- | --- |
| instanceId | 访问地址中`workbench/xxx/agentdest`中间的字符串（xxx即为实例ID），请参照下图： ![image](https://help-static-aliyun-doc.aliyuncs.com/assets/img/zh-CN/3483485171/p785290.png) | string |
| dom | 挂载元素的ID（**只需要在UI版本必填**）。 | string |

## config可选配置

### **UI版本专属配置**

| **参数** | **描述** | **类型** | **默认值** |
| --- | --- | --- | --- |
| header | 是否展示头部（"云联络中心"名称）。 | boolean | `true` |
| width | SDK面板的宽度（为了保证完整的UI展示，宽度最小310px）。 | string \\| number | `310px` |
| height | SDK面板的高度（为了保证完整的UI展示，高度最小540px）。 | string \\| number | `620px` |
| visible | 是否展示SDK面板。 | boolean | `true` |
| mainContentVisible | 是否展示SDK面板完整内容，设置`false`则只展示最简单功能的SDK工具条。 | boolean | `true` |
| offlineImage | 下线展示的静态图片地址。 | string | 系统默认 |
| breakImage | 小休展示的静态图片地址。 | string | 系统默认 |
| containerStyle | 自定义外层样式。 | [React.CSSProperties](https://github.com/DefinitelyTyped/DefinitelyTyped/blob/master/types/react/index.d.ts#L2383) | \\- |
| functionSwitch | 面板上的功能开关（是否显示），部分配置还需要在工作台上开启。 | [WorkbenchUIFunctionSwitch](#32287e05c6hkr) | 参考下方类型说明 |
| reducePanelContainer | 最小化面板的容器，会渲染到该容器上。 | Function() => HTMLElement | 默认在dom参数的ID标签中渲染 |
| defaultLastSelectedCallerNumber | 默认选择上次选择的外呼号码，在重新上下线时，默认再次选中上次使用的外呼号码。 | boolean | `true` |
| exportErrorOfApi | Toast提示接口的错误信息、“ApiName”、“ErrorCode”、“RequestId”，当接口出现错误时，提供错误信息， 便于后端排查问题。默认是"false"，可根据需要是否Toast错误消息。 | boolean | `false` |
| prettyPhoneNumber | 是否格式化显示电话号码。 如：`01012345678`会格式化显示为`010-12345678`。 | boolean | `true` |

#### **WorkbenchUIFunctionSwitch**

| **参数** | **描述** | **类型** | **默认值** |
| --- | --- | --- | --- |
| showToggleStatus | 显示左上角切换状态操作，包括最小化时左边的展示。 | boolean | `true` |
| breakAction | 显示左上角状态切换里的【小休】操作。 | boolean | `true` |
| offlineAction | 显示左上角状态切换里的【下线】操作。 | boolean | `true` |
| invisibilityAction | 显示左上角状态切换里的【隐身】操作。 | boolean | `true` |
| adjustVolumeSetting | 显示右上角设置中【音量调节】操作。 | boolean | `true` |
| deviceDetectSetting | 显示右上角设置中【设备检测】操作。 | boolean | `true` |
| accessModeSetting | 显示右上角设置中【接入模式】操作。 | boolean | `true` |
| accessPointSetting | 显示右上角设置中【坐席接入点】操作，**当 "isEnableSwitchAdapter: true" 时生效。** | boolean | `true` |
| showFlashSmsConfig | 显示右上角设置中【闪信配置】操作，当前配置生效的前提是配置过闪信运营商。 | boolean | `true` |
| allowStartConference | 允许坐席发起会议。 | boolean | `true` |
| allowMonitoring | 允许发起监听。 **此选项开启以后还需要管理员或者技能组组长权限，坐席权限就算设置此项也不能发起监听。** | boolean | `true` |
| allowCallOutbound | 允许坐席外呼电话。 | boolean | `true` |
| allowViewRecord | 允许坐席查看【通话记录】。 | boolean | `true` |
| allowViewMyWork | 允许坐席查看【我的工作】。 | boolean | `true` |
| reducePanel | 显示界面右上角最小化按钮。 | boolean | `true` |
| closeable | 显示右上角面板关闭按钮。 | boolean | `true` |
| showSpeechToText | 显示语音转文本按钮。 **说明** **该配置也需要在云联络中心>语音业务>设置>智能化设置中开启。** | boolean | `true` |
| allowCreateTicket | 允许坐席创建工单。 | boolean | `true` |
| allowCreateSessionSummary | 允许坐席创建会话小结。 | boolean | `true` |
| aiAssistantConfig | aiAssistantConfig: {object}允许坐席使用AI助手配置。 aiAssistantConfig.summary: {boolean} 会话小结和标签是否允许使用AI助手。 aiAssistantConfig.ticket: {boolean} 工单是否允许使用AI助手。 **说明** **该配置也需要在云联络中心>语音业务>设置>智能化设置中开启。** | object | `{summary: true,ticket: true}` |
| allowTransfer | allowTransfer: {boolean \\| object}允许坐席发起转接。 allowTransfer: {boolean} 是否允许所有转接方式。 allowTransfer.initiateAttendedTransfer: {boolean} 是否允许咨询转接。 allowTransfer.blindTransfer: {boolean} 是否允许直接转接。 | boolean \\| object | `true` |

### **通用配置**

**说明**

通用配置是UI版本和核心版本都适用的配置。

| **参数** | **描述** | **类型** | **默认值** |
| --- | --- | --- | --- |
| regionId | 云呼服务器部署的集群，如果没有特殊说明，为`cn-shanghai`。 | string | "cn-shanghai" |
| afterCallRule | 挂机后进入空闲状态的时间，单位为秒，默认为15秒；等待客服手动从话后处理切换到空闲状态，为"manual"；默认为客服工作台设置的值。 | number \\| 'manual' | 工作台配置 |
| autoAnswerCall | 有来电时自动接听电话的时长，单位为秒，默认为客服工作台设置的值。 | number | 工作台配置 |
| useLocalStorageToCall | 是否允许使用多标签页外呼。 | boolean | `false` |
| pollFrequenceWithoutWS | 当坐席状态WebSocket连接失败时，调用[PollUserStatus](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-polluserstatus)来拉取坐席状态的频率， 默认值为1000，单位毫秒。 目前云联络中心采用双通道方式来保证坐席状态的实时性与准确性：WebSocket推送和REST API拉取。 | number | `1000` |
| pollFrequenceWithWS | 当坐席状态WebSocket连接成功时，调用[PollUserStatus](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-polluserstatus)来拉取坐席状态的频率，（兜底策略以及心跳）。 默认值为10000，单位毫秒。 | number | `10000` |
| pollSaveWebRtcInfoFrequence | 轮询接口[SaveWebRtcInfo](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-savewebrtcinfo)的轮询频率， 默认值为10000，单位为毫秒。 | number | `10000` |
| disableSaveStats | 默认为false（不关闭收集通话录音数据）。收集坐席侧通话录音数据，方便出现问题时进行语音排查和网络分析。 强烈不建议关掉，当出现问题时不方便工程师排查。 | boolean | `false` |
| customizedNotification | 支持集成客户自主定制来电桌面提醒，默认显示云联络中心配置的桌面来电提醒，默认为`false`，传值为`true`时不展示。 | boolean | `false` |
| isEnableSwitchAdapter | 为提高坐席语音通话质量，新增多个接入点语音专线，默认为`true`。如果坐席需要直连云联络中心服务器，可设置为`false`。 | boolean | `true` |
| allowCalleeEncryption | 是否允许被叫号码加密传输（call方法的callee参数类型不做限制）。 | boolean | `false` |
| isMonitoredWithoutPerception | 坐席是否无感知被监听，当设置为`true`时，通话页面上不展示监听者信息。 | boolean | `false` |
| ringingToneSrc | 自定义来电铃声，HTML`audio`标签的`src`属性。 | string | 系统默认 |
| isOutboundNotReceivedToBeProcessed | 是否在外呼时未接听也流转到话后处理（当前是未接通后到话后处理状态，再立即到空闲状态）。 | boolean | `false` |
| videoCallConfig | 视频坐席相关配置。 | [VideoCallConfig](#76590d9d047f2) | 参考下方类型说明 |
| imConfig | IM 聊天插件的配置，需要加载IM SDK资源。 | [IMConfig](#0ce6354e8904k) | 参考下方类型说明 |
| transferDisplayedCustomerNumber | 在转接外部号码时选择外显客户号码。 | boolean | `false` |
| logger | 日志配置： logger.builtinEnabled: {boolean} 启动内置日志打印（使用console打印到浏览器调试控制台）， logger.level: {number} 日志等级，0(error)，1(warn)，2(log)，3(debug)， logger.connector: {(level: string, category: string, label: string \\| undefined, content: any) => void} 工厂函数，所有日志都经过这个方法处理。 | object | \\- |

#### **请求服务端接口的API地址及请求参数配置**

**说明**

请求路径为：`` `${ajaxOrigin}${ajaxPath}?${ajaxApiParamName}=${apiName}&product=CloudCallCenter&version=2020-07-01&region=${regionId}` ``。

| **参数** | **描述** | **类型** | **默认值** |
| --- | --- | --- | --- |
| ajaxOrigin | 请求源，默认请求当前源。 | string | location.origin |
| ajaxPath | 请求路径。 | string | "/data/api.json" |
| ssePath | sse接口的请求路径。 | string | "/sseApi" |
| ajaxApiParamName | 指定区分action的名称。 | string | "action" |
| ajaxMethod | 请求方式，post\\|get。 | "post" \\| "get" | "post" |
| ajaxOtherParams | 其他自定义参数和request同一层级。 | object | \\- |
| ajaxHeaders | 请求的headers。 | object | {'Content-Type': 'application/x-www-form-urlencoded'} |
| withCredentials | 表示跨域请求时是否需要使用凭证,是否允许携带cookie。 | boolean | false |
| apiAxiosFunc | 支持客户自己写请求接口的方法，最终返回结果为一个promise对象且返回的数据格式要和云联络中心公有云数据接口返回格式一致。 注意： 因为云联络中心内部使用axios请求库，默认返回的结果数据结构是： ``` { data: { code: "xxx", data: "xxx", httpStatusCode: "xxx", requestId: "xxxx" } } ``` 如果不是使用axios的话，请确保return的数据是这种数据结构，比 http 请求中返回的值多一个data包裹。 | function | \\- |

#### VideoCallConfig

| **参数** | **描述** | **类型** | **默认值** |
| --- | --- | --- | --- |
| enable | 是否启动视频通话。 | boolean | `false` |
| customVideoNode | 自定义显示视频组件： customVideoNode.localVideo: {HTMLVideoElement} 本地视频 DOM， customVideoNode.remoteVideo: {HTMLVideoElement} 远程视频 DOM。 **无UI版本该参数必填。** **video dom需要添加 autoplay 属性来启动自动播放，localVideo 需要添加 muted 属性禁止播放声音（防止重音）。** | object | \\- |
| disabledResize | 禁止调整视频窗口大小。 | boolean | `false` |
| defaultEnableCamera | 默认开启摄像头。 | boolean | `true` |
| getContainer | 默认将弹窗插入 document.body.div 下，可自定义将弹窗放在的哪个容器里面。 | () => HTMLElement | \\- |
| defaultSize | 默认视频窗口的宽高： defaultSize.width: {number} 宽度， defaultSize.height: {number} 高度。 | object | `{width: 1024, height: 576}` |
| cacheSize | 是否存储上次调整的视频窗口尺寸。 | boolean | `true` |
| minConstraints | 窗口大小的调整的最小宽高约束 \\[宽, 高\\]。 | \\[number, number\\] | `[768, 432]` |
| maxConstraints | 窗口大小的调整的最大宽高约束 \\[宽, 高\\]。 | \\[number, number\\] | `[1280, 720]` |
| isFixed | 是否是`position: fixed`布局。 | boolean | `true` |
| defaultPosition | 默认显示在屏幕中的位置，不设置默认屏幕正中，有缓存配置的话，使用缓存中的位置（需 cachePosition=true）。 defaultPosition.x: {number}， defaultPosition.y: {number}。 | object | 屏幕正中 |
| disabledDrag | 视频窗口是否禁止拖拽移动。 | boolean | `false` |
| cachePosition | 是否存储上次调整的位置，下次来电视频弹窗默认为上次的位置。 | object | `true` |
| setIncomingCallPrompt | 设置来电提示语，默认：“xxx邀请您进行视频通话”。 | (details: { callContext: object }) => string | \\- |
| containerBackground | 容器的背景 css background 属性。 | string | `#374151` |
| operationControl | 操作控制按钮： operationControl.microphone: {boolean} 是否静音， operationControl.camera: {boolean} 是否开启摄像头， operationControl.fullscreen: {boolean} 是否全屏。 | object | `{microphone: true,camera: true,fullscreen: true`} |

#### **IMConfig**

| **参数** | **描述** | **类型** | **默认值** |
| --- | --- | --- | --- |
| getContainer | IM插件的显示容器（**必填**）。 | () => HTMLElement | \\- |
| user | 自定义坐席信息，默认取【云联络中心>我的工作台>设置】中的头像和昵称参数。 user.nickname: {string} 名称， user.avatarUrl: {string} 头像。 | object | 系统配置 |
| onConvChange | 激活的会话改变事件，为null时，没有激活会话。 **签名：** Function(conv: object \\| null) => void **参数：** conv: {object} 会话信息。 | Function | \\- |
| onConvInvite | 会话邀请事件。 **签名：** Function(event: object) => void **参数：** event: {object} 会话附加信息。 | Function | \\- |
| onConvCancelInvite | 取消会话邀请事件。 **签名：** Function(event: object) => void **参数：** event: {object} 会话附加信息。 | Function | \\- |
| onConvReleased | 会话结束事件。 **签名：** Function(event: object) => void **参数：** event: {object} 会话附加信息。 | Function | \\- |
| onMessageAdd | 消息新增事件。 **签名：** Function(message: object) => void **参数：** message: {object} 消息详情。 | Funciton | \\- |
| onClaimQueueAdd | 队列中的消息增加事件。 **签名：** Function(claimQueueList: array) => void **参数：** claimQueueList: {Array<object>} 新增的待认领会话列表。 | Function | \\- |

### **钩子函数**

| **参数** | **描述** |
| --- | --- |
| onInit | SDK对象实例化完成时触发。 **签名：** Function() => void |
| onRegister | SIP服务注册成功时触发。 **签名：** Function(event: object) => void **参数：** event: {object} [GetLoginDetails](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-getlogindetails#api-detail-table-response-200.schema.properties.Data-name)接口返回的登录信息数据。 |
| onLogIn | 签入、上线时触发。 **签名：** Function(event: object) => void **参数：** event.chooseSkillGroupList: {array} 上线时选择的技能组列表。 |
| onLogOut | 退出登录时触发。 **签名：** Function() => void |
| onBreak | 小休时触发。 **签名：** Function(event: object) => void **参数：** event.breakReason: {string} 小休原因。 |
| onReady | 空闲时触发。 |
| onChangeInvisibility | 隐身状态切换。 **签名：** Function(invisibility: boolean) => void **参数：** invisibility: {boolean} \\`true\\`为当前是隐身状态，\\`false\\`为当前是非隐身状态。 |
| onCallComing | 来电时触发。 **签名：** Function(event: object) => void **参数：** event.caller: {string} 主叫号码。 event.callee: {string} 被叫号码。 event.jobId: {string} 当前通话ID。 event.callType: {string} 呼叫类型，参考[轮询坐席状态](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-polluserstatus#api-detail-table-response-200.schema.properties.Data.properties.CallContext.properties.ChannelContexts.items.properties.CallType-name)参数类型。 event.callContext: {object} 当前通话的详细信息，参考[PollUserStatus](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-polluserstatus#api-detail-table-response-200.schema.properties.Data-name)接口返回的数据类型。 |
| onBeforeCallDialing | 调用call方法前触发，如果配置这样一个钩子函数，**一定要执行callback方法**，否则电话不会被拨打出去。 **签名：** Function(event: object) => void **参数：** event.callee: {string} 被叫号码。 event.userId: {string} 坐席ID。 event.callback: {Function(callee?: string) => void} 满足条件以后的回调函数，可传入修改后的\\`callee\\`，不传为\\`event.callee\\`。 |
| onCallDialing | 去电、拨号振铃时触发。 **签名：** Function(event: object) => void **参数：** event.caller: {string} 主叫号码。 event.callee: {string} 被叫号码。 event.jobId: {string} 当前通话ID。 event.callType: {string} 呼叫类型，参考[轮询坐席状态](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-polluserstatus#api-detail-table-response-200.schema.properties.Data.properties.CallContext.properties.ChannelContexts.items.properties.CallType-name)参数类型。 event.callContext: {object} 当前通话的详细信息，参考[PollUserStatus](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-polluserstatus#api-detail-table-response-200.schema.properties.Data-name)接口返回的数据类型。 |
| onCallEstablish | 通话建立连接时触发。 **签名：** Function(event: object) => void **参数：** event.callContext: {object} 当前通话的详细信息，参考[PollUserStatus](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-polluserstatus#api-detail-table-response-200.schema.properties.Data-name)接口返回的数据类型。 |
| onBeforeCallHangup | 调用\\`hangUp\\`方法前触发，如果配置这样一个钩子函数，**一定要执行\\`callback\\`方法**，否则电话不会被挂断。 **签名：** Function(event: object) => void **参数：** event.jobId: {string} 当前通话ID。 event.channelId: {string} 这个坐席通话的channel id。 event.userId: {string} 坐席ID。 event.callback: {Function(jobId?: string, channelId?: string) => void}，表示满足条件以后的回调函数。 |
| onHangUp | 挂机时触发。 **签名：** Function(type：string) => void **参数：** type:{string} 挂机时的类型，具体为下述类型： - `ringing`：代表呼入未接时挂机。 - `dialing`：代表呼出未接时挂机。 - `inbound`：代表呼入通话，通话中挂断。 - `outbound`：代表呼出通话，通话中挂断。 - `agentHeld`： 代表咨询通话，通话中挂断。 - `meeting`：代表会议或会议中坐席状态变化，通话中挂断。 - `consulted`：代表被动求助（被咨询通话），通话中挂断。 - `monitored`：代表监听，通话中挂断。 - `monitoring`：代表发起监听，还未监听成功，通话中挂断。 - `bargedIn`：代表强插，通话中挂断。 - `coached`：代表耳语坐席，进入三方通话，通话中挂断。 |
| onCallRelease | 通话结束时触发。 **签名：** Function(event: object) => void **参数：** event.CallContext: {object} 当前通话的详细信息，参考[PollUserStatus](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-polluserstatus#api-detail-table-response-200.schema.properties.Data-name)接口返回的数据类型。 |
| onErrorNotify | 有一些错误信息会被触发，可以获取错误信息。 当处于开发阶段时建议在该钩子函数中打印参数，以获取错误信息。 **签名：** Function(event: object) => void **参数：** event.apiCode: {string} 当是API接口错误时，返回API接口报错的错误码，即接口返回的code。 event.errorCode: {string} 当是API接口错误时，返回接口action名称，否则返回系统定义的错误码。 event.errorMsg: {any} 详细错误信息。 event.errorMsgTip: {string} 错误信息提示。 event.requestId: {string} 当是API接口报错时，返回接口requestId参数。 |
| onStatusChange | 任何状态改变都会触发该函数，可在该函数内监听当前状态值的变化过程。状态code的含义请参考本文 [状态对照表及状态说明](#title-pzp-l48-41h)。 **签名：** Function(event: object) => void **参数：** event.code: {number} 当前状态码。 event.lastCode: {number} 上次状态码。 event.callContext: {object} 当前通话的详细信息，参考[PollUserStatus](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-polluserstatus#api-detail-table-response-200.schema.properties.Data-name)接口返回的数据类型。 |
| onWorkModeChange | 坐席默认有两种工作模式：场内模式和场外模式。当坐席配置了SIP话机后，还有办公电话模式。 **签名：** Function(workMode: string) => void **参数：** workMode: {string} 工作模式 - `ON_SITE`（场内模式）：通过浏览器接听、拨打电话。 - `OFF_SITE`（场外模式）：通过手机接听电话，即1.0中的“手机接听”方式。 - `OFFICE_PHONE`（办公电话模式）：通过SIP话机接听、拨打电话，无需通过浏览器操作。 |
| onDeviceTypeChange | 当坐席配置了SIP话机后，如果坐席通过浏览器上线，可选择使用哪种设备：WebRTC软电话和SIP话机。 **签名：** Function(deviceType: number) => void **参数：** deviceType: {number} 设备类型 - `0`：WebRTC软电话。 - `1`：SIP话机。 |
| onGetStatsData | 获取语音质量数据。 **签名：** Function(event: object) => void **参数：** event: {object} event.jobId: {string} 当前通话的ID。 event.callId: {string} 当前通话的话务ID。 event.connid: {string} 当前通话的话务序列ID。 event.sender: {RTCStatsReport} 具体参数类型参考 [RTCRtpSender.getStats()](https://developer.mozilla.org/en-US/docs/Web/API/RTCRtpSender/getStats)。 event.receiver: {RTCStatsReport} 具体参数类型参考 [RTCRtpReceiver.getStats()](https://developer.mozilla.org/en-US/docs/Web/API/RTCRtpSender/getStats)。 event.moss: {Array<number>} 语音质量评分，通话过程中，每秒多出一条（静音状态下不新增）。 |
| onAfterEarlyMediaRecognized | 有早媒体识别音时触发。 **签名：** Function(event: object) => void **参数：** event: {object} event.earlyMediaState: {string} 状态。 event.earlyMediaText: {string} 内容。 event.earlyMediaTime: {number} 时间。 event.releaseAfterEarlyMediaRecognized: {number} 识别到早媒体自动释放的时间（可在坐席控制台设置中配置）。 |
| onSignedSkillGroupChange | 签入技能组列表变化。 **签名：** Function(signedSkillGroupList: array, prevSignedSkillGroupList: array) => void **参数：** signedSkillGroupList: {array} 已签入技能组列表。 prevSignedSkillGroupList: {array} 上次签入的技能组列表。 |
| onAudioTranscriptionText | 语音转文字。 **签名：** Function(event: object) => void **参数：** event: {object} event.jobId: {string} 当前通话ID。 event.latestMessage: {object} 最新一条音转文消息。 event.messages: {Array<object>} 当前通话音转文的所有消息列表。 |
| onBeingMonitored | 当前坐席处于被监听状态时触发，监听者退出也触发。 **签名：** Function(event: object) => void **参数：** event: {object} event.isBeingMonitored: {boolean} 是否正在被监听。 event.monitorChannelContext: {object} 监听者的channel上下文信息。 |
| onIvrTrackingAISummary | 推送AI总结IVR轨迹分析结果事件。 **签名：** Function(event: object) => void **参数：** event: {object} event.jobId: {string} 当前通话ID。 event.result: {string} IVR轨迹分析结果。 event.success: {boolean} 是否分析成功。 |
| onMainContentVisibleChange | 【UI版本】`mainContentVisible` 参数改变事件。 **签名：** Function(visible: boolean) => void **参数：** visible: {boolean} 是否最大化，显示完整内容。 |
| onWorkbenchClose | 【UI版本】工作台右上角关闭按钮点击事件。 **签名：** Function() => void |
| onSelectCurrentCallRecord | 【UI版本】在通话记录列表页面，当前选中的通话记录。 **签名：** Function(event: object) => void **参数：** event: {object} event.record: {object} 选中的通话记录数据。 |
| onSelectOutboundNumber | 【UI版本】手动选择外呼号码时触发，\\`auto\\`时选择的自动。 **签名：** Function(caller: string) => void **参数：** caller: {string} 选择的主叫号码 |
| onMediaPlayFailed | 当媒体失败（浏览器自动播放策略阻止等原因）导致听不到客户声音时，需要在这个函数中做处理。 浏览器为了防止网页自动播放音视频对用户造成干扰，对音视频的自动播放功能做了限制：**在用户没有与网页产生交互（例如点击页面等）之前，带有声音媒体元素的网页将被禁止自动播放**（[Chrome中的自动播放策略](https://developer.chrome.com/blog/autoplay?hl=zh-cn)，[Safari中的自动播放策略](https://webkit.org/blog/7734/auto-play-policy-changes-for-macos/)）。 **签名：** Function(event: object) => void **参数：** event.mediaElement: {HTMLMediaElement} 获取播放的媒体元素，尝试手动play event.error: {Error} 媒体播放错误信息。 event.type: {string} `remote`：远程媒体；`ringTone`：来电响铃；`dtmfTone`：按键音；`hintTone`：提示音；`local`: 本地媒体。 |
| onHeartBeat | 新增对 `PollUserStatus` 轮询健康度的监听。在初始化时配置 `onHeartBeat` 回调即可接收。 **签名：** Function(event: object) => void **参数：** event.status：`success`（心跳成功）/ `failed`（单次失败，仍在重试）/ `stopped`（连续失败超阈值，已停止轮询） event.data：`status` 为 `success` 时返回 PollUserStatus 接口数据 event.errorMsg、event.requestId、event.failedCount: `status` 为 `failed` /`stopped`时返回错误信息、请求 ID 与累计连续失败次数 |

## SDK实例属性

| **属性** | **描述** | **类型** |
| --- | --- | --- |
| localMediaStream | 本地媒体流。如果呼叫未接听，则未定义。 外呼时：最初可在 `onCallDialing` 获取。 呼入时：最初可在 `onCallEstablish` 获取。 | MediaStream |
| remoteMediaStream | 远程媒体流。如果呼叫未接听，则未定义。 外呼时：最初可在 `onCallDialing` 获取。 呼入时：最初可在 `onCallEstablish` 获取。 | MediaStream |
| RTCPeerConnection | 对等WebRTC连接。如果对等连接已关闭，则未定义。 **警告** **【危险操作】对此属性做操作可能会导致通话出问题，包括（无声、延迟等）。** | [RTCPeerConnection](https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection) |

## **SDK实例方法**

**说明**

参数类型前面是 “?:” 表示该参数的传递是可选的，不必填，除非特殊说明。

### **UI版本专属方法**

| **参数** | **描述** |
| --- | --- |
| changeUIConfig | 修改UI版本专属配置。 **签名：** Function(config: object \\| ((prevConfig: object) => object)) => void； *当config是Function时的config签名：Function(*prevConfig*: object) => object，返回当前config参数，并需要return新的config。* **参数：** config: {object \\| function} 参考[UI版本专属配置](#ba6e20a087bk6)，目前可修改的参数为： `header` `height` `width` `visible` `mainContentVisible` `offlineImage` `breakImage` `containerStyle` `defaultLastSelectedCallerNumber` `exportErrorOfApi` 支持单个参数的修改。 |
| getUIConfig | 获取当前[UI版本专属配置](#ba6e20a087bk6)，只支持`changeUIConfig`方法可修改的参数。 **签名：** Function() => object **返回值：** 请参见 [UI版本专属配置](#ba6e20a087bk6) |
| changeFunctionSwitch | 修改UI功能开关配置参数（functionSwitch）。 **签名：** Function(config: WorkbenchUIFunctionSwitch \\| ((prevConfig: WorkbenchUIFunctionSwitch) => WorkbenchUIFunctionSwitch)) => void； *当config是Function时的config签名：Function(config:* WorkbenchUIFunctionSwitch*) =>* WorkbenchUIFunctionSwitch*，返回当前config参数，并需要return新的config。* **参数：** config: {WorkbenchUIFunctionSwitch \\| function} 参考[WorkbenchUIFunctionSwitch](#32287e05c6hkr) |
| getFunctionSwitch | 获取当前UI功能开关配置。 **签名：** Function() => WorkbenchUIFunctionSwitch **返回值：** WorkbenchUIFunctionSwitch: 参考[WorkbenchUIFunctionSwitch](#32287e05c6hkr) |
| reRender | 重新渲染界面，适用于单页面应用程序，挂载的dom销毁后，再重新渲染。 **签名：** Function() => void |
| setKeyboardValue | 设置拨号盘上的号码。 **签名：** Function(callee?: string, maskedCallee?: string) => void **参数：** callee?: {string} 被叫号码，显示在拨号盘上的输入框中。 maskedCallee?: {string} 被叫加密显示的号码（显示在坐席呼出详情里的号码）。 |

### **通用方法**

| **参数** | **描述** |
| --- | --- |
| isAvailBrowser | 此方法用来检测当前浏览器是否支持使用SDK。 **签名：** Function() => Promise<boolean> |
| checkNetwork | 此方法用来检测当前网络连接是否能连接到SDK网络服务，检测是否被本地的防火墙拦截。 **签名：** Function() => Promise<boolean> |
| getSkillGroups | 获取技能组列表。 **签名：** Function() => object **返回值：** chooseSkillGroupList: 已选择签入的技能组列表。 allSkillGroupList: 坐席所属的所有技能组列表，在`onInit`钩子函数触发后，才有正确的数据。 |
| getTurnServerList | 获取接入点列表，在`onInit`钩子函数触发后，才有正确的数据返回。 **签名：** Function() => Promise<array> **返回值：** 请参见[GetTurnServerList](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-getturnserverlist#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| register | 首次签入。页面加载完毕，首次签入需调用该方法。 **签名：** Function(options?: object) => Promise<UserContext> **参数：** - options.currentSkillGroups?: {Array<object>} 当前需要签入的技能组，可以从 `getSkillGroups` 方法中获取可签入的技能组（**UI版本**不填会弹出选择技能组弹窗；**非UI版本**不填则必须在【坐席工作台-语音业务-设置-坐席工作台-坐席设置】中将“**选择技能组登录**”项设置为“**否**”，**否则必填**）。 - options.accessPoint?: {string} 接入点region，从`getTurnServerList`方法的返回值中选取一个，自动选择传`default`，SDK内部实现选择延迟最低的接入点。 - options.deviceType?: {0 \\| 1} 设备类型，默认为 \\`0\\`，软电话注册上线，当坐席注册了SIP话机，可设置参数为\\`1\\`，指定SIP话机上线。 - options.mode?: {enum} 登录模式，可选值：'normal'、'invisibility'、'break'，分别为正常、隐身模式、小休模式。 - options.breakReason?: {string} 小休模式上线时的小休原因。 **返回值：** UserContext: 参考[SignInGroup](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-signingroup#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| logIn | 签入（处于签出状态可调用，状态为\\`1\\`），调用该方法实现上线操作。 **说明** 首次签入请使用register。 **签名：** Function(options?: object) => Promise<UserContext> **参数：** - options.currentSkillGroups?: {Array<object>} 当前需要签入的技能组，可以从 `getSkillGroups` 方法中获取可签入的技能组，不传默认使用register时签入的技能组。 - options.mode?: {enum} 登录模式，可选值：'normal'、'invisibility'、'break'，分别为正常、隐身模式、小休模式。 - options.breakReason?: {string} 小休模式上线时的小休原因。 **返回值：** UserContext: 参考[SignInGroup](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-signingroup#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| forceToPrepareSignIn | 如果注册时收到**7001**错误，即已有设备在线，可以调用此方法继续注册。成功后会把原有设备踢下线。 **签名：** Function() => Promise<UserContext> **返回值：** UserContext: 参考[SignInGroup](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-signingroup#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| logOut | 签出，调用该方法实现下线操作。 **签名：** Function() => Promise<UserContext> **返回值：** UserContext: 参考[SignOutGroup](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-signoutgroup#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| applyForBreak | 申请小休，设置后来电将不会转到当前坐席，会转到其他空闲的坐席人员。 **签名：** Function(breakReason?: string) => Promise<UserContext> **参数：** breakReason?: {string} 小休原因。 **返回值：** UserContext: 参考[TakeBreak](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-takebreak#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| ready | 置空闲、通过该方法可变为空闲状态，空闲状态后可接听、拨打电话。IM可以接受分配和认领会话。 **签名：** Function(options?: object) => Promise<UserContext> **参数：** options.invisible?: {boolean} 空闲时是否隐身。 **返回值：** UserContext: 参考[ReadyForService](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-readyforservice#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| changeVisibility | 隐身模式切换。如果为true，则坐席不会有电话呼入，也不会有IM会话分配。 **签名：** Function(invisible?: boolean) => Promise<UserContext> **参数：** invisible?: {boolean} 是否隐身。 **返回值：** UserContext: 参考[SignInGroup](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-signingroup#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据 |
| call | 拨打电话。 **签名：** Function(options?: object) => Promise<UserStatusContext> **参数：** - options.callee: {string} 被叫号码，如果是内部呼叫，该字段填写目标坐席的分机号，如果是外呼呼叫，填写客户的电话号码。 - options.caller?: {string} 主叫号码，如果是内部呼叫，这此参数无效，如果是外部呼叫，此参数为当前坐席可用的外呼号码。 - options.timeoutSeconds?: {number} 超时时间，呼叫在经过该参数指定的时间仍然未接通的情况下，则主动挂断，取值范围30-300，单位秒。 - options.maskedCallee?: {string} 脱敏后的被叫号码，如果该字段不为空，表示需要对被叫号码脱敏，脱敏规则由客户自行定义。 - options.mediaType?: {string} 媒体类型，默认是语音（AUDIO）, 其他可选参数包括 VIDEO。 **返回值：** UserStatusContext: 参考[MakeCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-makecall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| redialCall | 重拨电话，使用jobId拨打，一般用于被叫号码加密的通话。 **签名：** Function(options?: object) => Promise<UserStatusContext> **参数：** - options.jobId: {string} 通话ID。 - options.callee?: {string} 被叫号码，当前jobId通话的被叫号码。 - options.caller?: {string} 主叫号码。 - options.timeoutSeconds?: {number} 超时时间，呼叫在经过该参数指定的时间仍然未接通的情况下，则主动挂断，取值范围30-300，单位秒。 **返回值：** UserStatusContext: 参考[RedialCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-redialcall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| agentToAgent | 内部通话方法。 **签名：** Function(extension: string) => Promise<UserStatusContext> **参数：** extension: {string} 坐席分机号。 **返回值：** UserStatusContext: 参考[MakeCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-makecall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| answer | 接听电话，通过该方法可接听来电，建立通话连接。 **签名：** Function() => Promise<UserStatusContext> **返回值：** UserStatusContext: 参考[AnswerCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-answercall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| hangUp | 挂断/拒接，通过该方法可结束通话。 **签名：** Function(jobId?: string, channelId?: string) => Promise<UserStatusContext> **参数：** jobId?: {string} 可挂断指定通话。如果不传，则挂断当前通话。 channelId?: {string} 可挂断指定通话中的指定方。如果不传，则挂断当前通话。 **返回值：** UserStatusContext: 参考[ReleaseCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-releasecall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| stayAfterCall | 保持话后处理状态（与通话结束，点击话后处理按钮效果一致）。 **签名：** Function() => Promise<void> |
| sendDtmf | DTMF按键交互，发送dtmf。 **签名：** Function(options?: object) => Promise<UserStatusContext> **参数：** - options.dtmf: {string} DTMF按键信息，即拨号盘上的按键，包括0-9、\\*、#。 - options.jobId?: {string} 通话ID，多方通话时，必填。 - options.channelId?: {string} 待发送 DTMF 的话务通道 ID，多方通话时，必填。 **返回值：** UserStatusContext: 参考[SendDtmfSignaling](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-senddtmfsignaling#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| callHold | 通话保持/暂停通话，通过该方法可使通话进行保持，客户端听到的是一段音乐，坐席端说话客户端无法听到。 **签名：** Function() => Promise<UserStatusContext> **返回值：** UserStatusContext: 参考[HoldCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-holdcall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| callRetrieve | 通话取回，通过该方法结束通话保持的状态，重新建立客户端和坐席端的通话。 **签名：** Function() => Promise<UserStatusContext> **返回值：** UserStatusContext: 参考[RetrieveCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-retrievecall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| muteAgent | 坐席通话中静音，关闭麦克风。 **签名：** Function() => Promise<UserStatusContext> **返回值：** UserStatusContext: 参考[MuteCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-mutecall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| unmuteAgent | 坐席取消通话中静音，开启麦克风。 **签名：** Function() => Promise<UserStatusContext> **返回值：** UserStatusContext: 参考[UnmuteCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-unmutecall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| changeRingToneVolume | 改变来电振铃时的音量。 **签名：** Function(volume: number) => void **参数：** volume: {number} 音量，值为\\[0, 1\\]的数。 |
| changeVolumeInCall | 改变通话中的音量。 **签名：** Function(volume: number) => void **参数：** volume: {number} 音量，值为\\[0, 1\\]的数。 |
| thirdCallTransfer | 通话过程中直接转接，A和B通话，将通话直接交给C，直接转接也叫盲转或单步转。 **签名：** Function(options?: object) => Promise<UserStatusContext> **参数：** - options.transferee: {string} 被转接方，可以是坐席分机号或技能组ID或外部号码。 - options.transferor?: {string} 转接发起方，当场景是直接转接到外部号码时，用此参数指定的号码作为主叫，转内部坐席或技能组时，此参数无效，发起方由UserId指定。 - options.callPriority?: {number} 转接到技能组队列时的排队优先级，取值范围0-9，0优先级最高，9最低。 - options.strategyName?: {string} 转接到技能组队列时的座席分配策略名称，可选值为 MOST\\_IDLE，MOST\\_SKILLED，MOST\\_ACQUAINTED，CUSTOMIZED。 - options.strategyParams?: {string} 转接到技能组队列时的座席分配策略参数。 - options.timeoutSeconds?: {number} 超时时间，取值范围30-300，单位秒。 - options.transfereeType?: {string} 转接目的类型，可选值为 AGENT，SKILL\\_GROUP，IVR 和 EXTERNAL\\_NUMBER。 - options.contactFlowVariables?: {string} 传递给联系流的变量，这里配置的变量，可以在 IVR 流程中拿到并使用，格式为 JSON 字符串格式的键值对集合。 **返回值：** UserStatusContext: 参考[BlindTransfer](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-blindtransfer#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| initiateAttendedTransfer | 通话过程中咨询转接，A和B通话，咨询C，咨询过程中A等待，咨询转接也叫关注转或双步转。 **签名：** Function(options?: object) => Promise<UserStatusContext> **参数：** - options.transferee: {string} 被转接方，可以是坐席分机号或技能组ID或外部号码。 - options.transferor?: {string} 转接发起方，当场景是直接转接到外部号码时，用此参数指定的号码作为主叫，转内部坐席或技能组时，此参数无效，发起方由UserId指定。 - options.callPriority?: {number} 转接到技能组队列时的排队优先级，取值范围0-9，0优先级最高，9最低。 - options.strategyName?: {string} 转接到技能组队列时的座席分配策略名称，可选值为 MOST\\_IDLE，MOST\\_SKILLED，MOST\\_ACQUAINTED，CUSTOMIZED。 - options.strategyParams?: {string} 转接到技能组队列时的座席分配策略参数。 - options.timeoutSeconds?: {number} 超时时间，取值范围30-300，单位秒。 - options.transfereeType?: {string} 转接目的类型，可选值为 AGENT，SKILL\\_GROUP，IVR 和 EXTERNAL\\_NUMBER。 - options.contactFlowVariables?: {string} 传递给联系流的变量，这里配置的变量，可以在 IVR 流程中拿到并使用，格式为 JSON 字符串格式的键值对集合。 **返回值：** UserStatusContext: 参考[InitiateAttendedTransfer](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-initiateattendedtransfer#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| thirdCallRetrieve | 三方通话取回，回到原来的通话，A和B通话，咨询C，咨询完成回到A和B通话。 **签名：** Function() => Promise<UserStatusContext> **返回值：** UserStatusContext: 参考[CancelAttendedTransfer](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-cancelattendedtransfer#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| thirdCallTransferFinished | 三方咨询通话过程中转移通话，A和B通话，咨询C，咨询完成回到A和B通话，实现A和C通话。 **签名：** Function() => Promise<UserStatusContext> **返回值：** UserStatusContext: 参考[CompleteAttendedTransfer](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-completeattendedtransfer#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| switchToConference | 咨询通话转会议（多方通话）。 **签名：** Function() => Promise<UserStatusContext> **返回值：** UserStatusContext: 参考[SwitchToConference](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-switchtoconference#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| startConference | 发起会议。 **签名：** Function(options?: object) => Promise<UserStatusContext> **参数：** - options.participantListJson: {string} 参会方列表，格式为JSON数组的字符串，数组元素是参会方，如果是内呼坐席， 参会方是目标的坐席分机号，如果是外呼客户，参会方是客户号码。 - options.timeoutSeconds?: {number} 超时时间，取值范围30-300，单位秒。 **返回值：** UserStatusContext: 参考[StartConference](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-startconference#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| monitor | 监听方法。 **签名：** Function(userId: string) => Promise<UserStatusContext> **参数：** userId: {string} 需要监听的坐席ID。 **返回值：** UserStatusContext: 参考[MonitorCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-monitorcall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| bargeIn | 强插方法。成功后，转入三方会议模式。 **签名：** Function(options?: object) => Promise<UserStatusContext> **参数：** - options.jobId: {string} 被强插的通话ID。 - options.bargedUserId: {string} 被强插的座席ID。 - options.timeoutSeconds?: {number} 强插超时时间，经过指定的时间强插仍未成功，则取消强插，正常情况下，强插操作会马上成功， 设置超时时间是为了防止异常发生，此字段选填，默认30，单位秒。 **返回值：** UserStatusContext: 参考[BargeInCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-bargeincall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| intercept | 强拆方法，成功后，原坐席被踢出通话，新插入坐席与客户通话。 **签名：** Function(options?: object) => Promise<UserStatusContext> **参数：** - options.jobId: {string} 被强拆的通话ID。 - options.interceptedUserId: {string} 被强拆的座席ID。 - options.timeoutSeconds?: {number} 强拆超时时间，经过指定的时间强拆仍未成功，则取消强拆，正常情况下，强拆操作会马上成功， 设置超时时间是为了防止异常发生，此字段选填，默认30，单位秒。 **返回值：** UserStatusContext: 参考[InterceptCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-interceptcall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| coach | 辅导方法（耳语坐席）。管理员和技能组组长可以辅导坐席与客户通话。 成功后，客户只能听到初始坐席的声音，被辅导坐席可以同时听到客户和辅导者的声音。辅导者可以同时听到客户和坐席的声音。 **签名：** Function(options?: object) => Promise<UserStatusContext> **参数：** - options.jobId: {string} 被辅导的通话ID。 - options.coachedUserId: {string} 被辅导的座席ID。 - options.timeoutSeconds?: {number} 辅导超时时间，经过指定的时间辅导仍未成功，则取消辅导，此字段选填，默认30，单位秒。 **返回值：** UserStatusContext: 参考[CoachCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-coachcall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| cancelAutomaticCallRelease | 取消外呼智能挂机设置（“设置-坐席工作台-坐席接听-外呼智能挂机”中配置）的自动挂机操作。 **签名：** Function() => Promise<UserStatusContext> **返回值：** UserStatusContext: 参考[CoachCall](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-coachcall#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| transferStatisfic | 发送语音满意度,或者转到其他IVR流程。 **签名：** Function(contactFlowId?: string) => Promise<UserStatusContext> **参数：** contactFlowId?: {string} 如果不传，则发起已配置的语音满意度流程。也可以传入指定IVR流程ID，发起指定IVR流程。发起IVR流程后，当前坐席被挂断。 **返回值：** UserStatusContext: 参考[LaunchSurvey](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-launchsurvey#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| launchShortMessageAppraise | 送短信满意度，只有在话后处理状态下可用。 **签名：** Function(options?: object) => Promise<UserStatusContext> **参数：** options.smsMetadataId?: {string} 表示短信满意度配置ID，如果不传，则发起已配置的短信满意度模板。 **返回值：** UserStatusContext: 参考[LaunchSurvey](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-launchsurvey#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| launchShortMessageMissedCall | 发送语音满意度，或者转其他IVR流程。 **签名：** Function(options?: object) => Promise<void> **参数：** options.smsMetadataId?: {string} 短信满意度配置ID，如果不传，则会使用已配置的漏话短信模板。 |
| launchAuthentication | 核身验证，发送指定IVR流程，当前坐席不被挂断。 **签名：** Function(contactFlowId: string，contactFlowVariables?: string) => Promise<UserStatusContext> **参数：** - contactFlowId: {string} IVR 核身流程的联系流 ID。 - contactFlowVariables?: {string} 传递给联系流的变量，这里配置的变量，可以在 IVR 流程中拿到并使用，格式为 JSON 字符串格式的键值对集合。 **返回值：** UserStatusContext: 参考[LaunchAuthentication](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-launchauthentication#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| applyForOnSite | 设置场内模式。当坐席为场外模式时，可调用此方法设置场内模式后上线。 **签名：** Function() => Promise<UserContext> **返回值：** UserContext: 参考[ChangeWorkMode](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-changeworkmode#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| applyForOffSite | 设置场外模式。当坐席空闲时，可调用此方法设置场外模式，即手机接听。 **签名：** Function(options?: object) => Promise<UserContext> **参数：** - options.signedSkillGroupIdList?: {Array<string>} 需要签入的技能组ID列表。可以通过此参数指定场外座席需要签入的技能组列表。不传的话，核心版本会默认使用上次签入时的技能组，UI版本会显示弹窗选择签入技能组。 - options.mobile?: {string} 坐席的个人电话号码，该号码在场外模式下会用到， 坐席可以使用该号码进行场外模式接听，不传的话，使用坐席详情中手机号码/固话参数。 **返回值：** UserContext: 参考[ChangeWorkMode](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-changeworkmode#api-detail-table-response-200.schema.properties.Data-name)接口返回参数数据。 |
| applyForOffSiteDirectly | 直接申请场外模式，不显示弹窗确认。核心版本该方法与 `applyForOffSite` 方法完全一致，UI版本，不传`signedSkillGroupIdList`，也不显示选择技能组弹窗，与核心版本的`applyForOffSite`方法效果一致。 签名、参数、返回值都与 applyForOffSite 一致。 |
| getStatusCode | 获取坐席当前状态码。 **签名：** Function() => object **返回值：** code: {string} 当前状态。 lastCode: {string} 上一次状态。 |
| testTurnServers | 检测坐席接入点。 **签名：** Function(options?: object) => Promise<object> **参数：** - options.accessPoint?: {string} 可以只测某个接入点的值。不传为测试当前所有接入点。 - options.currentFrequence?: {number} 测试几次，不传为1次。多次取平均值。 **返回值：** - result: {object} 计算的节点数据。 - accessPoint: {string} 计算出延迟最低的节点。 |
| switchAccessPoint | 切换接入点. **签名：** Function(accessPoint: string) => void **参数：** accessPoint: {string} 需要切换的接入点。 |
| getSoftPhoneDeviceId | 获取当前软电话id。可以根据此值进行MakeCall接口调用。 **签名：** Function() => string |
| toggleLocalVideo | 本地摄像头开关。 **签名：** Function(enabled: boolean) => Promise<void> **参数：** enabled: {boolean} 是否开启。 |
| getAudioDeviceList | 获取当前设备的麦克风和耳机列表。 **签名：** Function() => Promise<MediaDeviceInfo\\[\\]> **返回值：** MediaDeviceInfo: 参考[MediaDeviceInfo](https://developer.mozilla.org/en-US/docs/Web/API/MediaDeviceInfo)。 |
| getVideoDeviceList | 获取当前设备的摄像头列表。 **签名：** Function() => Promise<MediaDeviceInfo\\[\\]> **返回值：** MediaDeviceInfo: 参考[MediaDeviceInfo](https://developer.mozilla.org/en-US/docs/Web/API/MediaDeviceInfo)。 |
| switchVideoInputDevice | 切换摄像头设备，在下一通视频通话生效。 **签名：** Function(deviceId: string) => void **参数：** deviceId: {string} 摄像头设备ID，可以通过getVideoDeviceList方法获取。 |
| setAudioInputDevice | 设置麦克风设备。 **签名：** Function(deviceId: string) => void **参数：** deviceId: {string} 麦克风设备ID，可以通过getAudioDeviceList方法获取。 |
| setAudioOutputDevice | 设置麦扬声器/耳机设备。 **签名：** Function(deviceId: string) => void **参数：** deviceId: {string} 扬声器设备ID，可以通过getAudioDeviceList方法获取。 |
| addSignedSkillGroup | 新增签入的技能组。 **签名：** Function(options?: object) => Promise<void> **参数：** - options.skillGroupList?: {Array<object>} 需要签入的技能组列表，核心版本必传，UI版本不传的话，会弹出选择技能组弹窗进行选择。 - options.mediaTypeList?: {Array<string>} 需要签入的技能组媒体类型，不传选择所有媒体类型**（只在UI版本支持该参数）。** |
| renderIM | 渲染IM插件（需要加载IM SDK）。 **签名：** Function() => void |
| unmountIM | 卸载IM插件（需要加载IM SDK），离线时自动卸载。 **签名：** Function() => void |
| unloadWorkbench | 卸载SDK工作台，此方法调用后，**必须重新初始化实例。** **签名：** Function() => Promise<void> |
| setCallerPhoneNumber | 设置当前坐席外呼号码。 **签名：** Function(phoneNumber: string) => void **参数：** phoneNumber: {string} 可外呼的号码，或者`auto`自动选择外呼号码 |
| getCallerPhoneNumber | 获取当前坐席外呼号码。 **签名：** Function() => string **返回值：** 返回当前坐席设置的外呼号码，`auto`是自动选择外呼号码 |

## **SDK静态方法**

**说明**

静态方法直接使用`window.CCCWorkbenchSDK`调用，如：

`window.CCCWorkbenchSDK.addListener('onInit', () => { console.log('实例已经初始化') })`。

| **参数** | **描述** |
| --- | --- |
| addListener | 监听钩子函数触发。 **签名：** Function(event: string, fn: (...args: any\\[\\]) => void, options: object) => void **参数：** event: {string} 钩子函数名称，具体查看[钩子函数](#f56cdc74389sz)。 fn: {Function} 钩子函数触发时调用的函数。 options?.once: {boolean} 是否只触发一次。 **示例：** ``` window.CCCWorkbenchSDK.addListener('onInit', () => { console.log('实例已经初始化'); }); ``` |
| removeListener | 删除指定钩子函数监听。 **签名：** Function(event: string, fn?: (...args: any\\[\\]) => void) => void **参数：** event: {string} 钩子函数名称，具体查看[钩子函数](#f56cdc74389sz)。 fn?: {Function} 钩子函数触发时调用的函数。 **示例：** ``` const onInitListener = () => { console.log('实例已经初始化'); }; // 添加监听器 window.CCCWorkbenchSDK.addListener('onInit', onInitListener); // 删除监听器 window.CCCWorkbenchSDK.removeListener('onInit', onInitListener); // 删除所有 onInit 监听器 window.CCCWorkbenchSDK.removeListener('onInit'); ``` |
| removeAllListeners | 删除所有钩子函数监听或者指定钩子函数监听。 **签名：** Function(event?: string) => void **参数：** event?: {string} 钩子函数名称，具体查看[钩子函数](#f56cdc74389sz)。 |

## **服务端准备工作**

因为SDK是嵌入到了您的自有业务系统中，在SDK的使用过程中，会发起多个请求到自有业务系统的服务端，请求的调用地址可以通过[请求服务端接口的API地址及请求参数配置](#bcd9b4f714rwt)来设置。需要将SDK发出的请求经过您的服务端转发到云联络中心的服务端（也就是调用云联络中心的openAPI），然后将返回结果透传回SDK中即可。详细步骤如下：

-   可以通过AK/SK方式请求接口（[AK版Demo参考](https://help.aliyun.com/zh/ccs/cccai/use-cases/accesskey-based-crm-demo)），或通过oauth2方式请求接口。
    
-   转发SDK发送的请求到云联络中心服务端，根据[API概览](https://help.aliyun.com/zh/ccs/cccai/developer-reference/api-ccc-2020-07-01-overview)调用对应openAPI，将返回结果透传回SDK即可，SDK所需的返回结果必须是JSON数据格式。
    
-   坐席，技能组等需要在云联络中心坐席控制台进行配置，否则无法正常工作。
    

| **类型** | **接口** | **描述** |
| --- | --- | --- |
| 业务接口 | GetLoginDetails | 获取坐席的登录信息。 |
| GetUser | 获取坐席的信息。 |
| ListSkillLevelsOfUser | 坐席的技能组信息。 |
| ListOutboundNumbersOfUser | 坐席的外呼号码。 |
| ListConfigItems | 坐席工作台配置信息。 |
| GetTurnServerList | 获取云呼提供的turn服务接入点。 |
| ListPrivilegesOfUser | 坐席的权限列表。 |
| GetTurnCredentials | Turn服务的账号密码。 |
| ListDevices | 登录的设备信息。 |
| PickOutboundNumbers | 自动选择外呼号码。 |
| GetNumberLocation | 查询号码归属地。 |
| ListRealtimeAgentStates | 查询当前坐席的状态列表（转接功能）。 |
| ListAgentStates | 查询当前的坐席列表（监听功能）。 |
| ResetAgentState | 重置坐席状态。 |
| ListRecentCallDetailRecords | 查询通话记录。 |
| ListSkillGroups | 获取技能组，只有admin有权限。 |
| ListBriefSkillGroups | 转接的技能组列表。 |
| ListHistoricalAgentReport | 获取坐席我的工作数据。 |
| SaveTerminalLog | 给服务端上报错误日志。 |
| SignInGroup | 技能组登录。 |
| PollUserStatus | 轮询获取用户状态。 |
| LaunchAuthentication | 核验身份。 |
| ChangeVisibility | 切换隐身。 |
| SignOutGroup | 退出。 |
| AddBlacklistCallTagging | 新增号码黑名单。 |
| AddFeedback | AI数据回流。 |
| AnalyzeConversation | 会话分析，生成AI内容。 |
| ListFlashSmsApplications | 获取闪信模板运营商列表。 |
| ListFlashSmsTemplates | 获取闪信模板列表。 |
| GetIvrTrackingSummary | 获取IVR智能分析结果。 |
| 话务接口 | TakeBreak | 小休。 |
| ReadyForService | 置空闲。 |
| MakeCall | 拨打电话。 |
| AnswerCall | 接听电话。 |
| ReleaseCall | 挂电话。 |
| HoldCall | 通话保持。 |
| RetrieveCall | 通话取回。 |
| BlindTransfer | 直接转接。 |
| InitiateAttendedTransfer | 发起咨询转接。 |
| CompleteAttendedTransfer | 咨询转接转移通话。 |
| CancelAttendedTransfer | 取消转接。 |
| SendDtmfSignaling | 发送DTMF按键。 |
| MonitorCall | 发起监听。 |
| BargeInCall | 监听状态下强插。 |
| InterceptCall | 监听状态下强拆。 |
| Coach | 监听状态下辅导。 |
| MuteCall | 静音。 |
| UnmuteCall | 取消静音。 |
| LaunchSurvey | 发送语音满意度。 |
| ChangeWorkMode | 切换工作模式。 |
| RedialCall | 回拨电话（通过jobId回拨，一般在号码加密的情况下调用）。 |

## **开发错误、操作逻辑错误**

SDK会抛出两种类型的错误：开发错误、操作逻辑错误。建议您在开发时配置onErrorNotify钩子并打印参数，方便排查问题并将相关错误抛出给客户，以便问题排查。

1.  开发错误：简单的说就是可以通过修改您的代码来修复的错误，是稳定重现的，这一类型的错误常见的有配置参数类型出错、调用SDK方法未按照状态约束表进行。比如配置项onInit要求是一个方法，但是却传入了一个字符串，那么SDK会直接执行如下代码，遇到这样的错误js执行被打断，必须要根据错误提示先进行修复。
    
2.  操作逻辑错误：这一类错误是用户在使用呼叫中心过程中一些操作不当造成的错误，不一定是稳定重现的，这一类型的错误常见的有未允许浏览器对本域名开启声卡权限、账号在别处登录、客服不在任何技能组中、呼叫中心网络错误等。这类错误SDK会调用onErrorNotify方法通知外部系统，钩子函数onErrorNotify中的所有情况：
    

```
  5001: '外呼失败',
  5002: '您尚未被加入到技能组中，暂时无法使用，请联系呼叫中心管理员添加',
  5003: '技能组信息异常',
  5004: '请检查坐席是否在通话中，并且设置了语音满意度流程',
  5005: '当前WebSocket连接缓慢，请等待或刷新后重新上线',
  5006: '请检查坐席是否在通话中，并且传入IVR流程ID',
  5007: '选择的技能组超出了限制',
  5008: '缺少技能组信息',
  6001: '没有通话Channel信息',
  6002: '没有通话ChannelID',
  6003: '没有通话JobID',
  7001: '已有设备注册，软电话未初始化', // 初始化sip之前检测出有设备，可以让客户选择是否登录
  7002: '已有设备注册，软电话初始化异常, 请刷新页面', // 初始化sip之后，注册设备和sip不一致，报错
  7003: '无法获取接入点信息',
  7004: '接入点测速失败',
  7005: '请使用http协议',
  7006: '浏览器不满足要求',
  7007: '现在有新设备上线，请检查',
  7008: 'SIP话机不在线',
  7009: '集群切换，所有接口不可用, 坐席需刷新页面',
  7010: '当前处于办公电话模式',
  8001: '请检查声卡权限', // 提示设备异常的界面
  8002: '请检查声卡权限', // 提示设备异常的界面
  8003: '已在通话中',
  8004: '来电铃声播放失败，请检查播放设备',
  8010: '检测到通话网络断开，请检查网络',
  8011: 'ice连接状态异常，请检查网络后，重新建立通话',
  8012: '通话建立时，ice协商失败',
  9001: '当前状态不能执行此操作',
  9002: '参数异常',
  9003: '执行失败',
  9004: '软电话已初始化好',
  9005: '请先调用PrepareSignIn方法',
  9006: '下线失败',
  9007: '网络连接失败',
  9008: '缺少登录信息',
  9009: '主叫为空',
  9010: '无可用主叫',
  9012: '被叫为空',
  9013: '参数异常',
  9014: '会议参加者错误，无两个参会人员',
  12001: '当前IM会话已被认领',
  /* 以下为迁出的event事件 */
  PollUserStatusError: '无法获取坐席状态，请重新登录',
```

### **5001 错误说明**

5001﻿错误中返回的errorMsg是外呼失败所对应的SIP Code，errorMsgTip是SIP Code所对应的语义翻译。

不同号码运营商所对应的SIP Code可能有所差异，这里列出常见SIP Code关系表：

```
{
  100: '正在呼叫中',
  180: '被叫正在振铃',
  181: '呼叫被转发',
  182: '正在排队中',
  183: '正在处理中',
  200: '成功',
  300: '多重选择，请求的地址有多个选择',
  301: '地址永久不可用，呼叫已重定向',
  302: '地址临时不可用，呼叫已重定向',
  305: '请求的资源必须通过Contact头域中指定的代理服务器访问',
  380: '替代服务，呼叫不成功，可以尝试另外的服务',
  400: '呼叫请求格式非法或语法错误',
  401: '用户未授权，需要进行用户认证',
  402: '需要付费才能完成会话',
  403: '服务器拒绝提供服务',
  404: '用户不存在，用户在Request-URL指定的服务器上不存在',
  405: '请求的方法不允许',
  406: '请求的资源只对某些特殊请求作出响应，对当前请求不接受',
  407: '需要进行用户认证',
  408: '请求超时，服务器未在规定时间内产生应答',
  409: '请求和当前资源状态产生冲突，请求不能被处理',
  410: '请求的资源在服务器上不存在且无法转发',
  411: '拒绝接受没有定义Content长度的请求',
  413: '请求太大，超出服务器处理上限',
  414: '请求URL太长，服务器拒绝请求',
  415: '服务器不支持请求的消息体格式，拒绝处理该请求',
  416: '不支持的URL计划',
  420: '服务器无法理解在Header中指出的扩展协议',
  421: '服务器需要特定的扩展来处理该请求，但扩展没有在请求中列出',
  423: '间隔太短，服务器在请求中设置的资源刷新时间（或者有效时间）过短',
  480: '被叫已联系上，但被叫方当前不可用',
  481: '服务器已接收到请求，但无法和现存的对话或事务匹配',
  482: '发现环路，服务器检测到一个循环',
  483: '跳数太多，请求包含的Max-Forwards头域为0',
  484: '服务器接收到请求，但Request-URL不完整',
  485: '请求的Request-URL不明确',
  486: '被叫已联系上，但被叫或运营商繁忙，暂时无法处理额外的呼叫',
  487: '请求终止，请求被BYE或CANCEL所终止，常见于主叫方主动取消呼叫的场景',
  488: '被叫无法接受请求，通常是媒体协商失败导致',
  491: '未决请求，在同一会话中，服务器收到的请求有一个依赖的请求正在处理',
  493: '不可辨识，服务器收到的请求包含一个加密的MIME，并且不知道或者没有提供合适的解密密钥',
  500: '运营商服务器内部错误',
  501: '运营商服务器没有实现相关的请求功能',
  502: '运营商服务器从下游服务器接收到一个非法的应答',
  503: '运营商服务器由于超负载或维护问题，暂时不能处理请求',
  504: '运营商服务器请求超时',
  505: '运营商服务器不支持请求中用到的SIP协议版本',
  513: '运营商服务器无法处理超过指定长度的消息',
  600: '被叫已联系上，但被叫处于忙状态，不打算接听电话',
  603: '被叫已联系上，但被叫明确不想应答或者不能加入通话，常见于被叫拉黑主叫的场景',
  604: '被叫离线，被叫不存在于网络中',
  606: '被叫已联系上，但会话描述的某些方面不被接收，媒体协商失败',
}
```

### **7001 错误说明**

```
7001错误中返回值示例：
{
  errorCode: 7001,
  errorMsg: {
     callId: '7089e388-b2db-e3b2-e4c2-572faf77c4d7',
     contact: 'sips:80001012@100.104.xx.xxx:15646;rtcweb-breaker=yes;transport=wss',
     deviceId: 'CCC-30.240.xx.xxx-chrome99-bs82ea17f7804263c',
     extension: '80001010',
     instanceId: 'ABC',
     userId: 'abc@ABC',
     userState: 'DIALING',
  },
  errorMsgTip: '已有设备注册，软电话未初始化'
}
参数说明：
deviceId：当前已登录的设备ID
userState：当前已登录设备状态。目前有以下状态：{
  TALKING: '通话中',
  DIALING: '拨号中',
  RINGING: '振铃中',
  WORKING: '话后处理',
  READY: '空闲',
  BREAK: '小休',
  OFFLINE: '下线',
}
```

当收到7001错误时，可调用[forceToPrepareSignIn](#7f46c51c1ankr)方法继续注册，并把原设备踢出。

## 状态对照表及状态说明

| **状态码** | **描述** | **操作** | **可允许调用的方法** |
| --- | --- | --- | --- |
| \\-1 | 未注册 | 当前状态只能操作register | register |
| 0   | 注册中 |     | register |
| 1   | 离线  | 上线  | logIn, applyForOffSite, forceToPrepareSignIn |
| 2   | 小休  | 置空闲，仅外呼，下线 | applyForBreak，ready, changeVisibility, logOut，addSignedSkillGroup |
| 3   | 空闲  | 下线、外呼、接听，发起监听，会议 | logOut, agentToAgent, call, monitor, applyForBreak, changeVisibility,bargeIn, intercept, coach, startConference，addSignedSkillGroup |
| 4   | 仅外呼 | 下线、外呼、接听、发起监听、会议、置空闲 | logOut, agentToAgent, call, monitor, applyForBreak，changeVisibility, ready，bargeIn, intercept, coach, startConference，addSignedSkillGroup |
| 5   | 话后处理 | 置空闲 | logOut, applyForBreak, ready, call, launchShortMessageAppraise, changeVisibility, applyForOffSite，addSignedSkillGroup |
| 6   | 振铃  | 接听  | answer |
| 7   | IM正在工作中 |     | addSignedSkillGroup |
| 8   | 拨号  | 挂断  | hangUp，sendDtmf |
| 9   | 呼入通话 | 挂断  | hangUp, callHold, callRetrieve, sendDtmf, muteAgent, unmuteAgent, transferStatisfic, launchAuthentication, thirdCallTransfer, initiateAttendedTransfer |
| 10  | 呼出通话 | 挂断  | hangUp, callHold, callRetrieve, sendDtmf, muteAgent, unmuteAgent, transferStatisfic, launchAuthentication, thirdCallTransfer, initiateAttendedTransfer |
| 11  | 内部通话 | 结束通话 | hangUp, callHold, callRetrieve, sendDtmf, muteAgent, umMuteAgent |
| 12  | 通话保持 | 取消通话保持 | callRetrieve |
| 16  | 发起三方 | 通话取回、取消三方通话 | thirdCallRetrieve |
| 17  | 咨询通话 | 取消咨询通话、咨询通话转移 | thirdCallRetrieve, thirdCallTransferFinished, sendDtmf, switchToConference |
| 19  | 会议  | 坐席由空闲状态发起会议 | hangUp, sendDtmf |
| 20  | 被动求助 | 挂断  | hangUp |
| 21  | 监听  | 挂断  | hangUp |
| 24  | 发起监听，还未监听成功 |     |     |
| 25  | 强插，进入三方通话 | 挂断  | hangUp |
| 26  | 耳语坐席，进入三方通话 | 挂断  | hangUp |
| 30  | 会议中坐席状态变化 | 例如有人退出会议，或者有人进入会议 | hangUp, transferStatisfic |

**说明**

1.  “可允许调用的方法”一列是列举部分话务或者与状态相关的方法，未列举的方法可以调用，但是结果在不同状态下可能有区别。
    
2.  状态变更可以通过[onStatusChange](#efa59da1b1l18)钩子函数获取，每次状态的变更都会触发。
    

## 多标签页外呼使用要点

### **使用场景**

做了CRM系统集成的用户，可以使用我们的SDK界面进行外呼，但是也存在一些用户需要在其他页面，比如一些用户列表或用户详情页面通过点击按钮进行外呼，这时就需要在该页面进行SDK注册，但是我们的SDK不支持多标签页注册，因此我们提供了**BroadcastChannel和LocalStorage**两个方案。

### **BroadcastChannel（推荐）**

通过 BroadcastChannel Web API 来在多个标签页中进行通信。分为主应用和子应用，使用 `window.CCCWorkbenchSDK.BroadcastChannelMain`注册主应用，`window.CCCWorkbenchSDK.BroadcastChannelChild`注册子应用。主应用的事件触发会通知给子应用，使子应用的事件也相对触发，子应用调用方法实际上是通知主应用调用方法，所以子应用的方法返回结果全部是Promise（即便在主应用中不是返回Promise），等待主应用调用方法成功。

BroadcastChannel相比于localStorage方案，支持大部分的钩子函数的触发和实例方法的调用。

#### **使用方法**

1.  主应用实例化，使用 `window.CCCWorkbenchSDK.BroadcastChannelMain`代替 `window.CCCWorkbenchSDK` 初始化实例，方法调用和参数传递和`window.CCCWorkbenchSDK`一致，如下：
    
    ```
    window.workench = window.CCCWorkbenchSDK.BroadcastChannelMain({
      instanceId: "xxx",
      /* 其他配置项 */
    });
    // window.CCCWorkbenchSDK.BroadcastChannelMain 前面不需要添加 new。
    ```
    
2.  子应用实例化，使用`window.CCCWorkbenchSDK.BroadcastChannelChild`初始化子应用，子应用参数传递只支持部分参数，包括 `instanceId`（必传）和钩子函数部分（`onGetStatsData` 不支持）的参数，其他参数传递无效。可调用主应用的方法（`getRemoteMediaStream` 不支持），方法返回Promise结果。参考如下：
    
    ```
    window.workbenchChild = window.CCCWorkbenchSDK.BroadcastChannelChild({
      instanceId: 'xxx',
      onInit: () => {
        console.log('主应用已初始化好！'); // 如果子应用在主应用onInit之后加载，则此事件不触发
        window.workbenchChild.register(); // 子应用调用register，使主应用注册上线
      },
    });
    
    window.workbenchChild.call({ callee: '199xxxx9999' }); // 拨打电话
    
    window.workbenchChild.hangUp(); // 挂断电话
    ```
    

#### **注意事项**

1.  **主应用和子应用必须在同一个浏览器。**
    
2.  主应用一个浏览器只能初始化一次，子应用可以多次多tab页。如果主应用多次的话，子应用调用的方法会通知给所有同实例ID的主应用，所有主应用都调用子应用的方法，可能会出现不符合预期的效果。
    
3.  BroadcastChannel Web API 的限制对主、子应用的通信同样有效。
    

### **LocalStorage**

在注册过SDK的标签页监听其他标签页localstorage的变化，在其他标签页设置localstorage来实现外呼。

#### **使用方法**

1.  设置配置项`useLocalStorageToCall`为`true`。
    
2.  首先所有标签页都要在同一个浏览器中，要求只有一个标签页注册CCCWorkbenchSDK，并保持该标签页的登录状态。
    
3.  在**其他标签页**拨打电话时设置一个localStorage（如果拨打电话页和注册页处于同一标签页，该方法将无法监听到，导致电话拨打不出去），key为CCCWorkbenchSDKCall，value为{callee: ‘1558888\*\*\*\*’, caller: ‘05712823\*\*\*\*’, random: 0.234234234}。其中caller的值具体设置参照上面SDK [call](#14dd43568etnj) 方法中的规定，设置成功以后，当注册过CCCWorkbenchSDK的标签页监听到localStorage的CCCWorkbenchSDKCall变化时，便自动外呼电话：
    
    ```
    const value = {
      callee: "1558888****",
      caller: "05712823****",
      random: Math.random(),
    };
    localStorage.setItem("CCCWorkbenchSDKCall", JSON.stringify(value));
    ```
    
4.  在其他标签页挂断电话时，需设置一个key为workbenchSdkHangup，value为一个随机数的localstorage，便自动挂断电话。
    
    ```
     localStorage.setItem('CCCWorkbenchSDKHangup',  Math.random())
    ```
    
5.  可通过`localStorage.getItem('CCCWorkbenchSDKStatus')`来查询当前坐席状态码，当值为3,4,5时才可以外拨号码；当值为8,9,10,11,12,21时才可挂断电话。
    

## **从2.x版本升级**

1.  前端资源地址有变化，集成方式分为UI版本与核心版本两种。
    
2.  全局SDK名称更改，由`WorkbenchSdk`改为`CCCWorkbenchSDK`。
    
3.  **强制**同时只能初始化（new）一次实例，重复初始化之前需要调用`unloadWorkbench`方法。
    
4.  **【Break Change】内部开发变量**`**window._sdk_app**`**已删除，请不要使用该变量。**
    
5.  **【Break Change】样式文件中去除全局样式，如 html、body、ul、li、a、img等元素的一些全局样式。**
    
6.  **config配置变更：**
    
    -   新增`functionSwitch`属性，使用`changeFunctionSwitch`方法可修改。
        
    -   新增`containerStyle`属性，自定义SDK界面容器样式（可修改圆角、阴影等样式）。
        
    -   新增`reducePanelContainer`属性，渲染最小化面板的容器，是一个返回一个HTML标签。
        
    -   新增`logger`属性，支持自定义日志收集与打印，便于业务方自主排查问题。
        
    -   更改`regionId`属性为可选值，默认为`cn-shanghai`。
        
    -   删除`defaultVisible`属性，使用`visible`替代。
        
    -   删除`defaultMainContentVisible`属性，使用`mainContentVisible`替代。
        
    -   删除`reducePanel`属性，使用`functionSwitch.reducePanel`替代。
        
    -   删除`isLoggedKeepBreak`属性，界面上可小休上线，register和logIn方法也支持mode="break"参数小休上线。
        
    -   删除`isLoggedInvisibility`属性，界面上可隐身上线，register和logIn方法也支持mode="invisibility"参数隐身上线。
        
    -   **【Break Change】删除属性**`**moreActionList**`**，由于界面的更改，功能菜单请使用**`**functionSwitch**`**属性。**
        
    -   **【Break Change】输出属性**`**sideNavList**`**，由于界面的更改，功能菜单请使用**`**functionSwitch**`**属性。**
        
7.  **钩子函数变更：**
    
    -   新增`onMainContentVisibleChange`钩子函数，在`mainContentVisible`改变的时候触发。
        
    -   新增`onWorkbenchClose`钩子函数，在**点击面板右上角关闭按钮**时触发。
        
    -   新增`onBeingMonitored`钩子函数，在被监听的时候触发。
        
    -   删除`onAgentOutboundScenario`钩子函数，使用`onChangeInvisibility`钩子函数代替，切换隐身时会触发。
        
    -   `onGetStatsData`钩子函数，新增`moss`参数，可表示坐席当前语音通话质量MOS评分。
        
8.  **实例方法变更：**
    
    -   所有异步方法都支持Promise（`call`、`hangUp`等），原有的callback依然支持，但是不再推荐使用callback。
        
    -   部分多参数传递的方法，目前合并为object类型传参，如register、logIn、call等。
        
    -   新增`changeUIConfig`方法，来修改UI部分的属性。
        
    -   新增`changeFunctionSwitch`方法，来修改`functionSwitch`属性。
        
    -   新增`addSignedSkillGroup`方法，在登录状态可签入新的技能组，而无需下线重新登录签入。
        
    -   删除`changeVisible`方法使用`changeUIConfig`来修改，例：`changeUIConfig({visible: true})`。
        
    -   删除`changeMainPaneVisible`方法使用`changeUIConfig`来修改，例：`changeUIConfig({mainContentVisible: true})`。
        
    -   删除`changeWidth`方法使用`changeUIConfig`来修改，例：`changeUIConfig({width: '310px'})`。
        
9.  **新增实例属性：**
    
    -   新增`localMediaStream`属性，获取本地媒体流。
        
    -   新增`remoteMediaStream`属性，获取远程媒体流。
        
    -   新增`RTCPeerConnection`属性，获取WebRTC对等连接。
        
10.  **业务逻辑变更：**
     
     -   **【Break Change】被监听者状态不变更为**`**21**`**，还是保持原来的状态码，页面上显示监听者的信息，被监听者可正常操作功能按键，使用**`**onBeingMonitored**`**钩子函数监听是否正在被监听。**`**21**`**仅表示监听者正在监听的状态。**
         

**说明**

除标记为“**【Break Change】**”的功能更改是不兼容2.x版本外，其他删除、变更等配置都兼容2.x版本，但是建议改为3.x版本的写法（在后续大版本升级时将会删除兼容2.x版本的逻辑）。

## 更新日志

### 2026.07.22

#### **workbench: 3.8.1**

**Features**

-   优化样式展示和交互体验
    
-   **添加** `**onHeartBeat**` **心跳事件**：可据此做掉线感知、自动重登或告警
    
-   **黑名单备注**：通话记录面板「加入黑名单」支持填写备注
    
-   **SIP 网络错误诊断增强**：异常 ICE 候选 / ICE 连接失败的错误提示补充排障建议（手机热点测试、联系 IT 开放 UDP 3478 端口等），并在错误通知中附带接入点、TURN 服务器、凭证是否过期等诊断信息，便于定位企业网络限制。
    

**Bug Fixes**

-   盲转 transferor 参数赋值：盲转（blindTransfer）中 `transferor` 赋值写错变量名，导致转接方参数未被正确置空，现修复，转接场景行为恢复正常
    

#### im-sdk: 1.8.1

-   添加黑名单能力
    
-   优化部分体验问题
    

### 2025.10.14

#### **workbench: 3.6.1**

**Features**

-   优化 `sendDtmf` 函数，增加 DTMF 发送队列处理逻辑，防止 DTMF 发送顺序不一致，出现意外情况
    
-   监听通道为列表形式以支持多通道监听，页面展示支持多个监听方信息展示
    

#### im-sdk: 1.6.0

-   优化编辑器部分功能
    
-   优化多图片发送显示进度效果
    

### 2025.08.21

#### **workbench: 3.5.2**

**Features**

-   新增 `[setCallerPhoneNumber](#7d8424aa9f9p3)`和 `[getCallerPhoneNumber](#a10fe179f8b51)` 两个实例方法，用于设置当前坐席外呼号码和获取当前外呼号码
    

**Bug Fixes**

-   修复界面样式异常的问题
    
-   修复 `defaultLastSelectedCallerNumber`字段设置无效的问题
    

### 2025.08.19

#### im-sdk**: 1.5.3**

**Bug Fixes**

-   优化排队中消息在坐席端的展示
    

### 2025.08.05

#### **workbench: 3.5.1**

**Features**

-   优化5001错误提示，根据不同的主叫号码供应商，【解决方案查询】按钮跳转到对应的供应商文档
    
-   优化更多操作按钮布局和键盘按钮界面样式
    

### 2025.04.24

#### **workbench: 3.4.1**

**Bug Fixes**

-   css文件头部添加 `@charset "UTF-8";`，防止浏览器使用其他编码解析文件导致部分ICON图标显示乱码。
    

### 2025.04.22

#### **workbench: 3.4.0**

**Features**

-   新增`prettyPhoneNumber`UI版本属性，以支持是否在界面上格式化显示电话号码。
    
-   支持在拨号响铃状态（8）下调用`sendDtmf`方法。
    
-   新增`functionSwitch.allowTransfer`属性，是否在界面上显示转接操作。
    
-   优化闪信配置获取逻辑，当 `functionSwitch.showFlashSmsConfig`设置为`false`时，不调用闪信配置接口。
    
-   `onSignedSkillGroupChange`钩子函数添加第二个参数（上一次签入的技能组列表）。
    
-   优化工作台卸载逻辑，`unloadWorkbench`方法改为异步Promise，当需要`unloadWorkbench`后立即重新初始化实例时，可以在等待异步结果执行完再初始化，避免某些异步操作未完成导致初始化异常。
    
-   部分错误提示的优化。
    

#### im-sdk: 1.4.2

-   修复部分已知问题。
    

### 2025.03.10

#### **workbench: 3.3.7**

**Bug Fixes**

-   处理并发会话的问题，同时只允许一个会话建立，新来电直接拒接，并提示8003错误消息。
    

### 2025.02.28

#### **workbench: 3.3.5**

**Bug Fixes**

-   修复SIP断线重连后，坐席状态异常，来电坐席状态不变更。
    
-   修复在挂机后请求`SaveWebRtcInfo`接口会异常，提示无`jobId`参数。
    

### 2025.02.14

#### **workbench: 3.3.4**

**Features**

-   添加 `onMediaPlayFailed` 钩子函数，当媒体失败（浏览器自动播放策略阻止）导致听不到客户声音时，需要在这个函数中做处理。
    

**Bug Fixes**

-   修复在7001错误时立即调用`forceToPrepareSignIn`方法，会出现坐席听不到客户声音的问题。
    

### 2025.01.14

#### **workbench: 3.3.2**

**Bug Fixes**

-   优化对 `apiAxiosFunc` 返回结果的检查逻辑，兼容返回值的异常情况。
    
-   修复配置【选择技能组登录】设置为否时，在某些情况下还是弹窗选择技能组。
    
-   优化对部分请求不触发`onErrorNotify`方法（部分日志记录接口，报错也不影响话务功能）。
    
-   优化SIP设备注册的轮询，防止因浏览器标签页置于后台setTimeout定时器延迟，导致坐席SIP设备注册超时而自动下线。
    

#### im-sdk: 1.2.2

**Bug Fixes**

-   修复视频转换功能异常的问题。
    
-   优化断线重连逻辑。
    

### 2024.12.25

#### **workbench: 3.3.1**

**Bug Fixes**

-   修复不加载imsdk资源时，初始化SDK失败。
    

### 2024.12.13

#### **workbench: 3.3.0**

**Features**

-   添加`addListener`、`removeListener`、`removeAllListeners` 等SDK静态方法，支持全局添加钩子函数监听器。
    

**Bug Fixes**

-   修复`exportErrorOfApi`使用`changeUIConfig`修改无效的问题。
    
-   修复 ws 重新连接逻辑，防止一直链接不上后重连频率激增，导致页面卡顿。
    

#### im-sdk: 1.2.0

**Features**

-   将不支持上传的文件格式打包为zip上传。
    
-   将不支持上传的视频格式转换为MP4上传，如以前不支持上传mov格式的视频，现在会转换为MP4格式上传。
    

### 2024.11.15

#### **workbench: 3.2.3**

**Bug Fixes**

-   修复缩小面板后拨打号码过程导致的样式异常问题。
    
-   兼容久振未接处理时，电话自动挂断触发onCallRelease钩子函数。
    
-   修复退出登录时，异常调用 ListFlashSmsSettings 接口的问题。
    

#### im-sdk: 1.1.5

**Bug Fixes**

-   修复草稿回显失败的问题。
    

### 2024.10.17

#### **workbench: 3.2.2**

**Bug Fixes**

-   修复某些情况下unloadWorkbench调用后，再次初始化register上线报错9001的问题。
    

### 2024.10.09

#### **workbench: 3.2.1**

**Features**

-   添加`ssePath`配置参数，支持sse接口EnhanceAgentReplies请求。
    
-   新增`onIvrTrackingAISummary`钩子函数，支持在来电响铃时，获取IVR智能分析结果数据
    
-   隐身状态下，管理员支持发起监听操作。
    
-   语音转文本页面中，支持显示IVR轨迹智能分析和通话结束后的通话智能分析信息（通话智能分析需要开通语音转写功能）。
    
-   闪信配置功能改版，支持技能组维度的闪信配置，支持记住上次选择的闪信模板。
    
-   外呼时新增分机号拨号，使用逗号（,）分割，逗号后是分机号。
    
-   外呼时，拨号盘支持长按输入星号。
    

#### im-sdk: 1.1.2

**Features**

-   新增智能回复辅助功能，AI扩写、AI纠错、话术优化（需要支持sse接口EnhanceAgentReplies调用）。
    
-   新增会话结束后显示智能会话分析卡片。
    
-   满意度消息卡片升级，样式优化。
    
-   全屏显示图片时，支持点击下载按钮下载。
    

### 2024.08.09

#### im-sdk: 1.0.**6**

**Bug Fixes**

-   修复获取客户历史消息时，视频消息的ur过期问题。
    

### 2024.08.01

#### **workbench: 3.1.4**

**Bug Fixes**

-   修复在onStatusChange事件中当前状态变为3时立刻调用call方法打电话，出现“无可用主叫”的错误。
    

### 2024.07.29

#### **workbench: 3.1.3**

**Bug Fixes**

-   对`register`和`startConference`方法的2.x版本传参形式做兼容，并添加废弃提醒。
    
-   修复在设置中配置自定义铃声无效的问题。
    
-   修复对Chrome72版本的兼容性。
    
-   修复当只有一个主叫号码时，通话记录中无重播按钮的问题。
    

**Features**

-   拨号时，界面上显示拨号中计时器。
    
-   添加通话过程中，主被叫号码点击复制功能。
    

**BreakingChanges**

-   **减少对全局公共样式的更改, 优化组件样式应用方式，去除** `***,::before,::after {}**` **等全局选择器样式。**
    

#### im-sdk: 1.0.5

**Bug Fixes**

-   优化部分样式的显示。
    

**Features**

-   添加快捷回复操作，需要管理员在【**网络业务**\>**设置**\>**工作台**\>**快捷回复**】中设置。
    
-   添加访客使用端和IP所在地址显示。
    
-   新增服务中列表排序功能。
    
-   已结束会话列表中，新增会话小结标识。
    

### 2024.07.17

#### **workbench: 3.1.0**

**Bug Fixes**

-   修复 onRegister 钩子函数参数传递异常的问题。
    

**Features**

-   优化多Tab页通信逻辑，添加 [BroadcastChannel](https://developer.mozilla.org/en-US/docs/Web/API/BroadcastChannel) 方案，支持钩子函数和大部分方法的调用。
    
-   优化内部逻辑，提升系统稳定性。
    

### 2024.07.01

#### **workbench: 3.0.9**

**Bug Fixes**

-   修复当被咨询时，不显示挂断按钮。
    
-   修复当被咨询时，挂断后的话后处理状态，显示会议界面。
    
-   修复设置页面配置【是否支持直接转接】无效的问题。
    
-   修复语音转文本面板客户号码显示（适配来电和去电号码隐藏的规则）。
    
-   修复在转接过程中，来电技能组丢失的问题。
    
-   修复logIn方法传入签入技能组参数`currentSkillGroups`无效。
    

#### im-sdk: 0.5.10

**Bug Fixs**

-   修复部分接口调用参数异常。
    

### **2024.06.25**

#### **workbench: 3.0.8**

**Bug Fixes**

-   修复在SIP话机模式下，不能发送满意度的问题。