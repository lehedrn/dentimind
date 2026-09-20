通过本文，您可以实现将坐席工作台嵌入到第三方系统中，直接在您的系统中实现单点登录、接打电话等功能，并且您可以通过监听SDK中的方法来实现来电弹屏。下面的工作需要您公司的前端工程师来实施。您可以随时关注该文档页面，SDK有更新时会及时更新文档页面。

**重要**

SDK 3.x 版本已发布，请移步[前端SDK文档接入（3.x）](https://help.aliyun.com/zh/ccs/cccai/use-cases/ccc-sdk-frontend-access-3)，查看接入文档，2.x版本迁移请查看[十二、从2.x版本升级](https://help.aliyun.com/zh/ccs/cccai/use-cases/ccc-sdk-frontend-access-3#dda7673269o0u)，2.x版本后续不再做新功能开发。

## 前端资源

**重要**

**更新前端资源版本以后，一定要在本地环境做全面测试以后再发布线上环境！**

```
<!-- IM sdk样式文件，不使用IM插件不要加载此文件-->
<link rel="stylesheet" type="text/css" href="https://g.alicdn.com/code/npm/@ali/cc-im-sdk/{version-im-sdk}/index.css">
<!-- 软电话sdk样式文件-->
<link rel="stylesheet" type="text/css" href="//g.alicdn.com/cloudcallcenter/web-workbench-sdk/{version-workbench}/main.min.css">

<!-- IM sdk js文件，不使用IM插件不要加载此文件-->
<script type="text/javascript" src="//g.alicdn.com/code/npm/@ali/cc-im-sdk/{version-im-sdk}/index.js"></script>
<!-- 软电话sdk js文件-->
<script type="text/javascript" src="//g.alicdn.com/cloudcallcenter-voip/web-agentbar-sdk/{version-agentbar}/index.js"></script>
<script type="text/javascript" src="//g.alicdn.com/cloudcallcenter/web-workbench-sdk/{version-workbench}/workbenchSdk.min.js"></script>
以上静态资源，把上面的{version-im-sdk}、{version-agentbar}和{version-workbench}替换为对应的版本号，当前最新版本号为：
version-im-sdk ==>    0.5.8 // 最新版本请前往3.x版本文档查看
version-agentbar ==>  2.4.0
version-workbench ==> 2.16.0 // 最新3.x版本，请前往更新
```

**重要**

-   **以上js文件必须按照顺序加载，有相互依赖的关系。只使用软电话SDK则不需要加载IM sdk的文件，但是只使用IM SDK的话，所有文件都必须加载。**
    
-   **如要兼容Android、iOS和Safari浏览器，请添加WebRTC相关补充库，例如被广泛支持的**[Adapter.js](https://github.com/webrtcHacks/adapter)**（在web-agentbar-sdk之前加载）。**
    

## 初始化SDK

接入SDK之前需要做以下工作：

1.  必须使用Chrome浏览器，版本号为58以上。原因是云联络中心的通话是通过WebRTC技术实现的，目前Chrome浏览器对WebRTC技术的支持是相对最好的。为了保证您的通话质量及安全性，所以我们做出了这样的要求。
    
2.  软电话SDK所嵌入的自有业务系统**必须使用HTTPS协议**。原因是chrome在47版本之后，禁止http协议获取系统麦克风权限，会造成无法正常通话。
    
3.  如果您是在iframe标签内使用软电话SDK，那么需要为iframe标签增加allow="microphone"属性，来允许iframe标签获取系统麦克风权限。
    

初始化SDK：

```
window.workbench = new WorkbenchSdk(config)
```

## config必选配置

-   **dom**
    
    ```
    挂载元素id。
    ```
    
-   **instanceId**
    
    ```
    创建云联络中心实例填写的域名， https://ccc.console.aliyun.com/AccV2Instance，访问地址中workbench/xxx/agentdest中间的字符串（xxx就是实例id）,参照下图：
    ```
    
    ![image](https://help-static-aliyun-doc.aliyuncs.com/assets/img/zh-CN/0404781571/p973724.png)
    
-   **regionId**
    
    ```
    云联络中心服务器部署的集群，如果没有特殊说明，为'cn-shanghai'。
    ```
    

## config可选配置

-   **header**
    
    ```
    是否展示头部（小休，下线，场外模式接听等），默认展示，参数类型：Boolean。
    ```
    
-   **width**
    
    ```
    宽度，默认320px，参数类型：Number。
    ```
    
-   **height**
    
    ```
    高度，默认580px，参数类型：Number；（为了保证完整的UI展示，建议高度最低580px）。
    ```
    
-   **defaultVisible**
    
    ```
    默认是否展示面板，默认为true，参数类型：Boolean。
    ```
    
-   **defaultMainContentVisible**
    
    ```
    默认是否展开软电话面板，默认为true，参数类型：Boolean。
    ```
    
-   **offlineImage**
    
    ```
    下线展示的静态图片地址，参数类型：String。
    ```
    
-   **breakImage**
    
    ```
    小休展示的静态图片地址，参数类型：String。
    ```
    
-   **afterCallRule**
    
    ```
    挂机后进入空闲状态的时间，单位秒，默认15秒，参数类型：Number。等待客服手动去从话后处理切换到空闲状态，为“manual”。
    ```
    
-   **autoAnswerCall**
    
    ```
    有来电时自动接听电话的时长，单位秒，默认为手动接听，参数类型：Number。
    ```
    
-   **isLoggedKeepBreak**
    
    ```
    是否在登录时保持小休状态（不想在业务繁忙时上线立即接电话可设置为true）。目前是登录时从小休默认自动变为空闲状态。
    ```
    
-   **isLoggedInvisibility** ***「version-workbench: 2.12.2」***
    
    ```
    是否在登录时保持隐身状态，目前登录时会处于
    ```
    
-   **isOutboundNotReceivedToBeProcessed**
    
    ```
    是否在外呼时未接听也流转到话后处理（当前是未接通后到话后处理状态，再立即到空闲状态）。
    ```
    
-   **exportErrorOfApi**
    
    ```
    Toast提示接口的错误信息、ApiName、ErrorCode、RequestId，当接口出现错误时，提供错误信息，便于后端排查问题。默认是false，可根据需要是否Toast错误消息。
    ```
    
-   **moreActionList**
    
    ```
    在头部的功能模块的按钮列表，值可为["online", "ready", "onlyCall", "break", "offline", "adjustVolume", "changeWorkMode"]，
    分别对应[上线, 结束小休, 隐身, 小休, 下线, 调节音量, 场外模式接听]，用户可根据需求选择配置项，参数类型：Array。
    默认值：["break", "offline", "adjustVolume", "changeWorkMode"]。
    ```
    
    **说明**
    
    面板收缩时，上面的值全部有效，面板展开时 \["online", "ready"\] 设置无效（不显示），操作按钮在可在面板中使用。
    
-   **useLocalStorageToCall**
    
    ```
    是否允许使用多标签页外呼，默认为false，参数类型：Boolean；详细介绍请参考第9条说明。
    ```
    
-   **pollFrequenceWithoutWS**
    
    ```
    当坐席状态WebSocket连接失败时，调用REST API来拉取坐席状态的频率。默认值为1000，单位毫秒，参数类型：Number。
    目前云联络中心采用双通道方式来保证坐席状态的实时性与准确性：WebSocket推送和Rest API拉取。
    ```
    
-   **pollFrequenceWithWS**
    
    ```
    当坐席状态WebSocket连接成功时，调用Rest API来拉取坐席状态的频率。默认值为10000，单位毫秒，参数类型：Number。
    ```
    
-   **pollSaveWebRtcInfoFrequence**
    
    ```
    SaveWebRtcInfo（存储通话信息）接口的调用频率；默认值为：10000，单位毫秒，参数类型：Number。最小值：2000。
    ```
    
-   **sideNavList**
    
    ```
    支持面板左侧导航显示自定义，默认是显示全部，配置以后显示自定义的导航，配置项：呼入, 呼出, 内部通话, 通话记录, 转接, 会议, 监听, 我的工作, 设备检测, 设置。
    ```
    
-   **disableSaveStats**
    
    ```
    默认为false（不关闭收集通话录音数据），参数类型：Boolean。收集坐席侧通话录音数据，方便出现问题时进行语音排查和网络分析。强烈不建议关掉，当出现问题时不方便工程师排查。
    ```
    
-   **reducePanel**
    
    ```
    SDK面板最小化Icon展示，默认为true，如果不需要该功能，可设置为false，参数类型：Boolean。
    ```
    
-   **isEnableSwitchAdapter**
    
    ```
    为提高坐席语音通话质量，新增多个接入点语音专线，默认为true。如果坐席需要直连云呼服务器，可设置为false，参数类型：Boolean。
    ```
    
-   **customizedNotification**
    
    ```
    支持集成客户自主定制来电桌面提醒，默认显示呼叫中心配置的桌面来电提醒，默认为false。传值为true时不展示，参数类型：Boolean。
    ```
    
-   **allowCalleeEncryption**
    
    ```
    是否允许被叫号码加密传输（call方法的callee参数类型不做限制）。
    ```
    
-   **defaultLastSelectedCallerNumber** ***「version-workbench: 2.12.2」***
    
    ```
    是否记住上次选中的主叫号码（存储在浏览器缓存中，下次上线默认选中）。
    ```
    
-   **imConfig**
    
    ```
    im 聊天的配置，需加载对应的css和js文件
    
    {
      /**
       * 坐席信息，默认是用工作台设置里面的昵称和头像
       */
      user?: {
            /**
             * 显示名称
             */
            nickname?: string;
            /**
             * 头像 URL
             */
            avatarUrl?: string;
        };
    
      /**
       * im 显示的容器
       */
      getContainer: () => HTMLElement;
    
      /**
       * 会话改变事件，为null时，没有激活会话
       * @param conv
       * @returns
       */
      onConvChange?: (conv) => void;
    
      /**
       * 会话邀请事件
       */
      onConvInvite?: (event) => void;
    
      /**
       * 取消会话邀请事件
       */
      onConvCancelInvite?: (event) => void;
    
      /**
       * 会话结束事件
       */
      onConvReleased?: (event) => void;
    
      /**
       * 消息添加事件
       */
      onMessageAdd?: (message) => void;
    
      /**
       * 队列消息添加事件
       */
      onClaimQueueAdd?: (event) => void;
    }
    ```
    

**以下参数是前端请求服务端接口的API地址及请求参数配置：**

**请求路径为：**${ajaxOrigin}${ajaxPath}?${ajaxApiParamName}=${apiName}&product=CloudCallCenter&version=2020-07-01&region=${regionId}

-   **ajaxOrigin**
    
    ```
    请求源，默认请求当前源（location.origin），参数类型：String。
    ```
    
-   **ajaxPath**
    
    ```
    请求路径，默认为"/data/api.json"。
    ```
    
-   **withCredentials**
    
    ```
    表示跨域请求时是否需要使用凭证,是否允许携带cookie,参数类型：Boolean。
    ```
    
-   **ajaxApiParamName**
    
    ```
    ajaxType为param时指定区分action的名称，默认action，参数类型：String。
    ```
    
-   **ajaxMethod**
    
    ```
    请求方式，post|get 默认post，参数类型：String。
    ```
    
-   **ajaxOtherParams**
    
    ```
    其他自定义参数和request同一层级，参数类型：Object。
    ```
    
-   **ajaxHeaders**
    
    ```
    请求的header，参数类型：Object。
    ```
    
-   **apiAxiosFunc**
    
    ```
    支持客户自己写请求接口的方法，最终返回结果为一个promise对象且返回的数据格式要和云呼叫中心公有云数据接口返回格式一致。
    apiAxiosFunc: (apiName, params) => {
       console.log(apiName, params);
       let promise = axios({
          method: 'post',
          url:`/aliyun/ccc/api?action=${apiName}`,
          headers: {
             'Content-Type': 'application/x-www-form-urlencoded',
          },
          data: Qs.stringify({ request: JSON.stringify(params)}),
        });
        return promise;
    }
    
    注意：
    因为云联络中心内部使用axios请求库，默认返回的是结果数据结构是：
    { 
      data: {
        code:xxx, 
        data: xxx, 
        httpStatusCode: xxx, 
        requestId: xxxx
      }
    }
    如果不是使用axios的话，请确保 return 的数据是这种数据结构，比 http 请求中返回的值多一个 data 包裹。
    ```
    

**至此，请求接口的参数配置结束。**

### **钩子函数**

以下是钩子函数，某些事件触发时的回调函数，类型均为function。

-   **onInit()**
    
    ```
    SDK对象实例化完成时触发。
    ```
    
-   **onRegister(config)**
    
    ```
    sip服务注册成功时触发。
    ```
    
-   **onLogIn()**
    
    ```
    签入、上线时触发。
    ```
    
-   **onLogOut()**
    
    ```
    签出、下线时触发。
    ```
    
-   **onBreak()**
    
    ```
    小休时触发。
    ```
    
-   **onReady()**
    
    ```
    空闲时触发。
    ```
    
-   **onAgentOutboundScenario**
    
    ```
    仅外呼时触发。
    ```
    
-   **onCallComing(callDetail)**
    
    ```
    来电时触发，可以在该函数内获取到一个对象callDetail，callDetail参数信息含义如下：
    caller：主叫号码。
    callee：被叫号码。
    callType：呼叫类型。
    jobId：当前通话的ID。
    callContext：当前通话的详细信息。
    ```
    
    **重要**
    
    为了提高接通率，当有来电振铃30s后未接听，会自动将当前坐席置为小休状态。电话自动流转回转人工队列，分配给其他空闲坐席。
    
-   **onBeforeCallDialing(payload)**
    
    ```
    调用call方法前触发，如果配置这样一个钩子函数一定要执行callback方法，否则电话不会被拨打出去。payload返回数据的参数含义如下：
    callee：被叫号码。
    userId：用户的userId。
    callback：满足条件以后的调用，可传入完参数callee：被叫前缀+被叫号码，不传为面板或call方法传入的被叫号码。
    ```
    
-   **onCallDialing(callDetail)**
    
    ```
    去电、拨号振铃时触发，可以在该函数内获取到一个对象callDetail，callDetail参数信息含义如下：
    caller：主叫号码。
    callee：被叫号码。
    callType：呼叫类型。
    jobId：当前通话的ID。
    callContext：当前通话的详细信息。
    ```
    
-   **onHangUp(type)**
    
    ```
    挂机时触发，参数type值：
    `ringing`: 代表呼入未接时挂机。
    `dialing`: 代表呼出未接时挂机。
    `inbound`: 代表呼入通话，通话中挂断。
    `outbound`: 代表呼出通话，通话中挂断。
    `internalcall`: 代表内部通话，通话中挂断。
    `agentHeld`: 代表咨询通话，通话中挂断。
    `meeting`: 代表会议或会议中坐席状态变化，挂断。
    `consulted`: 代表被动求助（被咨询通话），挂断。
    `monitored`: 代表监听，通话中挂断。
    `monitoring`: 代表发起监听，还未监听成功，挂断。
    `bargedIn`: 代表强插，通话中挂断。
    `coached`: 代表耳语坐席，进入三方通话，通话中挂断。
    ```
    
-   **onBeforeCallHangup(payload)**
    
    ```
    调用hangUp方法前触发，如果配置这样一个钩子函数一定要执行callback方法，否则电话不会被挂断。payload返回的参数含义如下：
    callback：回调方法。
    jobId：当前通话ID。
    channelId：这个坐席通话的channel id。
    userId: loginInfo.userId 。
    ```
    
-   **onCallEstablish(callDetail)**
    
    ```
    通话建立连接时触发，可以在该函数内获取到一个对象callDetail，callDetail参数信息含义如下：
    callContext：当前通话的详细信息。
    ```
    
-   **onCallRelease(callDetail)**
    
    ```
    通话结束时触发，可以在该函数内获取到一个对象callDetail，callDetail参数信息含义如下：
    callContext：当前通话的详细信息。
    ```
    
-   **onErrorNotify(error)**
    
    ```
    当有一些错误信息的时候触发，可以获取error信息，error参数含义如下：
    errorCode: 错误code。
    errorMsg: response错误信息。
    errorMsgTip: 我们定义的中文错误信息。
    requestId: 请求ID。
    apiCode: API请求的错误code。
    ```
    
    **说明**
    
    当处于开发阶段时建议在该钩子函数中打印参数表以获取错误信息。
    
-   **onStatusChange(codeDetail)**
    
    ```
    任何状态改变都会触发该函数，可在该函数内监听当前状态值的变化过程，状态code的含义请参考本文档第八条状态对照表。可以获取到codeDetail参数，codeDetail参数含义如下：
    code: 当前状态码。
    lastCode： 上次状态码。
    context：上下文信息。
    ```
    
-   **onWorkModeChange(workMode)**
    
    ```
    坐席默认有两种工作模式：场内模式和场外模式。当坐席配置了SIP话机后，还有办公电话模式。
    场内模式：通过浏览器接听、拨打电话。
    场外模式：通过手机接听电话，即1.0中的“手机接听”方式。
    办公电话模式：通过SIP话机接听、拨打电话，无需通过浏览器操作。
    workMode参数含义如下：
    "ON_SITE"：场内模式。
    "OFF_SITE"：场外模式。
    "OFFICE_PHONE"：办公电话模式。
    ```
    
-   **onDeviceTypeChange(deviceType)**
    
    ```
    当坐席配置了SIP话机后，坐席如果通过浏览器上线，可选择使用哪种设备：WebRTC软电话和SIP话机。
    参数deviceType类型为Number：
    0：WebRTC软电话。
    1：SIP话机。
    ```
    
-   **onGetStatsData(payload)**
    
    具体概念请参考[RTCPeerConnection.getStats()](https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/getStats)。
    
    ```
    可以订阅此钩子函数，获取通话中的通话语音质量。每秒返回一次数据。
    payload中包含：
    callId：当前通话的callId。
    sender：发送方数据。
    receiver：接收方数据。
    
    参考用法：
    sender && sender.forEach(report => {
     console.log('sender', report);
    }
    ```
    
-   **onSelectOutboundNumber(number)**
    
    ```
    /**
     * 面板中选择主叫号码事件
     *
     * @param {string} number 选择的主叫号码
     */
    onSelectOutboundNumber(number: string): void
    ```
    

-   **onSelectCurrentCallRecord(payload)**
    

`payload.record`可查看[ListRecentCallDetailRecords - 获取坐席最近通话记录列表](https://help.aliyun.com/zh/ccs/cccai/api-ccc-2020-07-01-listrecentcalldetailrecords)接口返回参数。

```
/**
 * 当前选中的通话记录
 */
onSelectCurrentCallRecord?(payload: {record: object}): void
```

-   **onAfterEarlyMediaRecognized(payload)**
    
    ```
    /**
     * 外呼智能挂机钩子函数，返回早媒体识别信息
     */
    onAfterEarlyMediaRecognized?(payload: {
                                 /**
                                  * 早媒体状态
                                  */
                                 earlyMediaState: string,
                                 /**
                                  * 早媒体开始的时间戳（便于倒计时计算）
                                  */
                                 earlyMediaTime: number,
                                 /**
                                  * 早媒体状态说明
                                  */
                                 earlyMediaText: string,
                                 /**
                                  * 在设置中添加的倒计时挂机时间
                                  */
                                 releaseAfterEarlyMediaRecognized: number
                                 })
    ```
    

#### **配置示例**

```
window.workbench = new window.WorkbenchSdk({
  dom: "workbench-container",
  regionId: "cn-shanghai",
  width: "320px",
  height: "552px",
  instanceId: "XXX",
  ajaxPath: "/aliyun/ccc/api",
  ajaxMethod: "post",
  afterCallRule: 15, // 挂机后的话后处理时间
  header: true,
  autoAnswerCall: 8, // 有来电振铃响8s后自动接听
  exportErrorOfApi: true,
  onInit() {
    // window.workbench.register() // 想实现自动上线在此注册
  },
  imConfig: {
    getContainer() {
      return document.getElementById('im-container');
    },
  },
  onLogIn() {
    // window.workbench.renderIM(); // 渲染IM组件
  },
  onLogOut() {
    // window.workbench.unmountIM(); // 卸载IM组件
  },
  onErrorNotify(error) {
    console.warn(error);
  },
  onCallComing(callDetail) {
    console.log(callDetail);
  },
  onCallDialing(callDetail) {
    console.log(callDetail);
  },
  onStatusChange(codeDetail) {
    console.log(codeDetail);
  },
  onCallEstablish(callDetail) {
    console.log("这里是通话建立时触发的回调函数", callDetail);
  },
  onCallRelease(callDetail) {
    console.log("这里是通话结束时触发的回调函数", callDetail);
  },
  onHangUp(type) {
    console.log(`这里是onHangUp事件，type = ${type}`);
  },
});
```

## SDK方法

以下调用方式为：window.workbench.方法名（传参）。

**重要**

**请注意初始化SDK时定义的全局变量名称是否与文档定义的一致。**

-   **isAvailBrowser()**
    
    ```
    此方法用来检测当前浏览器是否支持使用软电话的，若浏览器不兼容软电话，会弹出一个提示框并维持3s，
    并在钩子函数onErrorNotify中可得到错误信息提示；若支持则无弹框提示，onErrorNotify中也无错误信息。
    ```
    
-   **checkNetwork()**
    
    ```
    此方法用来检测当前网络连接是否能连接到软电话的服务，检测是否被本地的防火墙拦截。
    ```
    
-   changeVisible(visible)
    
    ```
    显示或隐藏软电话面板，参数visible类型为Boolean。
    ```
    
-   **changeMainPaneVisible(visible)**
    
    ```
    展开或折叠软电话面板，参数visible类型为Boolean。
    ```
    
-   **changeWidth(width)**
    
    ```
    设置软电话面板宽度。目前默认值为320px。参数width类型为Number。
    ```
    
-   **unloadWorkbench**
    
    ```
    删除已建立的Workbench实例，以供再次创建。
    ```
    
-   **reRender()**
    
    ```
    重新进行SDK的挂载，主要场景为在通话过程中或上线状态下切换到其他页面以后再回到坐席工作台界面，主要适用于SPA应用。
    ```
    
-   **register(loginSkillGroupArray, accessPoint, deviceType, mode, breakReason)**
    
    ```
    /**
     * 首次签入，包含了sip服务注册+签入+置空闲，页面加载完毕，首次签入需调用该方法，
     * 调用完成后坐席进入空闲状态（需要在onInit钩子方法执行之后才可以调用）
     *
     * @param loginSkillGroupArray 从接口`ListSkillGroupsOfUser`得到坐席的技能组列表信息
     * @param accessPoint 从接口`GetTurnServerList`获取的数组对象的`region`，
     * 必须和接口`region`保持一致，否则不能切换成功，自动传`default`，SDK内部实现选择最近的接入点。
     * @param deviceType 设备类型，可选参数，当坐席注册了SIP话机，可设置参数为`1`，指定SIP话机上线。
     * @param mode 登录模式
     * @param breakReason 小休模式上线的时候的小休原因
     */
    function register(
        loginSkillGroupArray?: any[],
        accessPoint?: string,
        deviceType?: number,
        mode?: LoginMode,
        breakReason?: string,
      ): void;
      
     /**
      * 登录后的状态
      * `normal`: 正常登录状态
      * `invisibility`: 隐身登录状态
      * `break`: 小休状态
      */
     type LoginMode = 'normal' | 'invisibility' | 'break';
    ```
    
-   **logIn(loginSkillGroupArray)**
    
    ```
    /**
     * 签入（处于签出状态可调用，状态为`1`），调用该方法实现上线操作
     *
     * @param loginSkillGroupArray 从接口`ListSkillGroupsOfUser`得到坐席的技能组列表信息
     * @param mode 登录模式
     * @param breakReason 小休模式上线的时候的小休原因
     */
    logIn(loginSkillGroupArray?: any[], mode?: LoginMode, breakReason?: string): void;
    ```
    
-   **logOut()**
    
    ```
    签出，调用该方法实现下线操作。
    ```
    
-   **ready()**
    
    ```
    置空闲、通过该方法可变为空闲状态，空闲状态后可接听、拨打电话。
    ```
    
-   **applyForBreak(breakReason, callback)**
    
    ```
    /**
     * 申请小休，设置后来电将不会转到当前坐席，会转到其他空闲的坐席人员。
     *
     * @param breakReason 默认是`default`，可自定义小休原因，方便统计不同的小休类型
     * @param callback 调用成功后的回调函数
     */
    applyForBreak(breakReason?: string, callback?: (e?: any) => void): void;
    ```
    
-   **applyForCallOnly(isCallOnly)**
    
    ```
    /**
     * 设置是否仅外呼。如果为true，则坐席不会有电话呼入。（请使用 changeVisibility 代替）
     *
     * @param isCallOnly 是否仅外呼
     */
    applyForCallOnly(isCallOnly: boolean): void;
    ```
    
-   **changeVisibility(invisible)** ***「version-workbench: 2.12.2」***
    
    ```
    /**
     * 隐身模式切换。如果为true，则坐席不会有电话呼入，（效果跟仅外呼一致）
     *
     * @param invisible 是否为隐身模式
     */
    changeVisibility(invisible: boolean): void;
    ```
    
-   **applyForOnSite()**
    
    ```
    设置场内模式。当坐席为场外模式时，可调用此方法设置场内模式后再调logIn方法上线。
    ```
    
-   **applyForOffSite()**
    
    ```
    设置场外模式。当坐席空闲时，可调用此方法设置场外模式，即手机接听。
    ```
    
-   **applyForOffSiteDirectly()**
    
    ```
    直接设置场外模式，不显示弹窗确认。当坐席空闲时，可调用此方法设置场外模式，即手机接听。
    ```
    
-   **getStatusCode()**
    
    ```
    /**
     * 获取坐席当前状态码。
     */
    getStatusCode(): {
      /**
       * 当前状态
       */
      code: number;
      /**
       * 上一次状态
       */
      lastCode: number;
    };
    ```
    
-   **hangUp(releaseJobId, releaseChannelId, callback)**
    
    ```
    /**
     * 挂断，通过该方法可结束通话。
     *
     * @param releaseJobId 可挂断指定通话。如果不传，则挂断当前通话。
     * @param releaseChannelId 可挂断指定通话中的指定方。如果不传，则挂断当前通话。
     * @param callback 调用成功后的回调函数
     */
    hangUp(releaseJobId?: string, releaseChannelId?: string, callback?: (e?: any) => void): void;
    ```
    
-   **answer(callback)**
    
    ```
    接听电话，通过该方法可接听来电，建立通话连接。
    callback: 调用成功后的回调函数，参数类型为Function。
    ```
    
-   **call(callee, caller, callback, otherParams)**
    
    ```
    拨打电话。
    callee：被叫号码，必传，数据类型是String。
    caller：主叫号码，可以指定主叫号码；也可以不传，或者传''或者‘auto’，根据外呼的号码的归属地选择与其同一归属地的主叫号码，若没有同一归属地的就随机在坐席绑定的外呼号码列表中随意选择一个。
    callback: 调用成功后的回调函数，参数类型为Function。
    otherParams: 可选参数，发起外呼时，可增加一些参数，目前支持的参数有：
      {
        TimeoutSeconds: 超时时间，呼叫在经过该参数指定的时间仍然未接通的情况下，则主动挂断。参数类型为Number
        Tags: 随路数据。参数类型为String。
        MaskedCallee: 脱敏后的被叫号码，例如"1318888****"。参数类型为String。
      }
    ```
    
-   **stayAfterCall**
    
    ```
    保持话后处理状态（与通话结束，点击话后处理按钮效果一致）。
    ```
    
-   **sendDtmf(number, jobId, channelId, callback)**
    
    ```
    不传 jobId和channelId 时，第二个参数为可为callback。
    /**
     * DTMF按键交互，发送dtmf。
     *
     * @param number 可为0~9，*或#
     * @param callback 调用成功后的回调函数
     */
    sendDtmf(number: string|number, callback?:(e:any) => void)
    
    /**
     * DTMF按键交互，发送dtmf。
     * 三方通话时，必须要传 jobId 和 channelId
     *
     * @param number 可为0~9，*或#
     * @param jobId 当前话务的 jobId
     * @param channelId 需要发送dtmf的 chennelId （可从 callContext 里面获取）
     * @param callback 调用成功后的回调函数
     */
    sendDtmf(number: string|number, jobId?: string, channelId?: string, callback?:(e:any) => void)
    ```
    
-   **callHold(callback)**
    
    ```
    通话保持，通过该方法可使通话进行保持，客户端听到的是一段音乐，坐席端说话客户端无法听到。
    callback: 调用成功后的回调函数，参数类型为Function。
    ```
    
-   **callRetrieve(callback)**
    
    ```
    通话取回，通过该方法结束通话保持的状态，重新建立客户端和坐席端的通话。
    callback: 调用成功后的回调函数，参数类型为Function。
    ```
    
-   **muteAgent()**
    
    ```
    通话中静音。
    ```
    
-   **unMuteAgent()**
    
    ```
    取消通话中静音。
    ```
    
-   **changeVolumeInCall(volumeInCall)**
    
    ```
    /**
     * 改变通话中的音量
     *
     * @param volumeInCall 值为[0, 1]的小数
     */
    changeVolumeInCall(volumeInCall: number): void;
    ```
    
-   **changeRingToneVolume(volumeInCall)**
    
    ```
    /**
     * 改变来电振铃时的音量
     *
     * @param volumeInCall 值为[0, 1]的小数
     */
    changeRingToneVolume(volumeInCall: number): void;
    ```
    
-   thirdCallTransfer(callee, caller, callback) *「version-workbench: <2.13.1」*
    
-   thirdCallTransfer(params) *「version-workbench: >=2.13.1」*
    
    ```
    /**
     * 通话过程中直接转接，A和B通话，将通话直接交给C
     *
     * @param params.callee 被叫号码 | 技能组ID
     * @param params.caller 主叫号码
     * @param params.callPriority 转接优先级，在转接技能组的时候可以传入，0-9（默认0 最高优先级）
     * @param params.strategyName 转接到技能组队列时的座席分配策略名称
     * @param params.strategyParams 转接到技能组队列时的座席分配策略参数
     * @param params.timeoutSeconds 直接转接超时时间，超过指定时间被转接方没有接起通话，则挂断通话，此字段选填，默认 30，单位秒
     * @param params.callback 调用成功后的回调函数
     *
     * @description
     * ```text
     * 转接给坐席
     * callee：坐席分机号
     * caller: ''
     *
     * 转接给外部电话
     * callee：手机号
     * caller：'auto'
     *
     * 转接给指定技能组
     * callee：技能组ID
     * caller：''
     * ```
     */
    thirdCallTransfer(params: {
        callee: string;
        caller?: string;
        callPriority?: number;
        strategyName?: string;
        strategyParams?: string;
        timeoutSeconds?: number;
        callback?: Callback;
      }): void;
    ```
    
-   initiateAttendedTransfer(callee, caller, callback)*「version-workbench: <2.13.1」*
    
-   initiateAttendedTransfer(params) *「version-workbench: >=2.13.1」*
    
    ```
    /**
     * 通话过程中咨询转接，A和B通话，咨询C，咨询过程中A等待
     *
     * @param params.callee 被叫号码 | 技能组ID
     * @param params.caller 主叫号码
     * @param params.callPriority 转接优先级，在转接技能组的时候可以传入，0-9（默认0 最高优先级）
     * @param params.strategyName 转接到技能组队列时的座席分配策略名称
     * @param params.strategyParams 转接到技能组队列时的座席分配策略参数
     * @param params.timeoutSeconds 直接转接超时时间，超过指定时间被转接方没有接起通话，则挂断通话，此字段选填，默认 30，单位秒
     * @param params.callback 调用成功后的回调函数
     *
     * @description
     * 
     * 转接给坐席
     * callee：坐席分机号
     * caller: ''
     *
     * 转接给外部电话
     * callee：手机号
     * caller：'auto'
     *
     * 转接给指定技能组
     * callee：技能组ID
     * caller：''
     */
    initiateAttendedTransfer(params: {
        callee: string;
        caller?: string;
        callPriority?: number;
        strategyName?: string;
        strategyParams?: string;
        timeoutSeconds?: number;
        callback?: Callback;
      }): void;
    ```
    
-   **thirdCallRetrieve(callback)**
    
    ```
    三方通话取回，回到原来的通话，A和B通话，咨询C，咨询完成回到A和B通话。
    callback: 调用成功后的回调函数，参数类型为Function。
    ```
    
-   **thirdCallTransferFinished(callback)**
    
    ```
    三方咨询通话过程中转移通话，A和B通话，咨询C，咨询完成回到A和B通话，实现A和C通话。
    callback: 调用成功后的回调函数，参数类型为Function。
    ```
    
-   **switchToConference(jobId)**
    
    ```
    /**
     * 咨询通话转会议（多方通话）
     * 
     * @param jobId 通话 id
     */
    switchToConference(jobId?: string): void;
    ```
    
-   **startConference(participantListJson, otherParams)**
    
    ```
    /**
     * 发起会议
     *
     * @param participantListJson 会议通话的另外两方，坐席的话传坐席的分机号，传参类型 `JSON.stringify(['1234567', '7654321'])`
     * @param otherParams 其他参数
     *
     * @example
     * ```js
     * startConference(JSON.stringify(['1234567', '7654321']))
     * ```
     */
    startConference(participantListJson: string, otherParams?: Record<string, any>): void;
    ```
    
-   **monitor(userId, callback)**
    
    ```
    /**
     * 监听方法
     *
     * @param userId 坐席的ID
     * @param callback 调用成功后的回调函数
     */
    monitor(userId: string, callback?: (result?: any) => void): void;
    ```
    
-   **bargeIn(userId, jobId, callback)**
    
    ```
    /**
     * 强插方法。成功后，转入三方会议模式。
     *
     * @param userId 坐席的ID
     * @param jobId 要插入的通话ID
     * @param callback 调用成功后的回调函数
     */
    bargeIn(userId: string, jobId?: string, callback?:(result?: any) => void): void;
    ```
    
-   **intercept(userId, jobId, callback)**
    
    ```
    /**
     * 强拆方法，成功后，原坐席被踢出通话，新插入坐席与客户通话。
     *
     * @param userId 坐席的ID
     * @param jobId 要插入的通话ID
     * @param callback 调用成功后的回调函数
     */
    intercept(userId: string, jobId?: string, callback?: (e?:any) => void): void;
    ```
    
-   **coach(userId, jobId, callback)**
    
    ```
    /**
     * 辅导方法。管理员和技能组组长可以辅导坐席与客户通话。
     * 成功后，客户只能听到初始坐席的声音，被辅导坐席可以同时听到客户和辅导者的声音。辅导者可以同时听到客户和坐席的声音。
     *
     * @param userId 坐席的ID
     * @param jobId 要辅导的通话ID
     * @param callback 调用成功后的回调函数
     */
    coach(userId: string, jobId?: string, callback?: (e?:any) => void): void;
    ```
    
-   **agentToAgent(userDN, callback)**
    
    ```
    /**
     * 内部通话方法
     *
     * @param userDN 坐席的分机号，为8位数字
     * @param callback 调用成功后的回调函数
     */
    agentToAgent(userDN: string, callback?: (e:any) => void): void;
    ```
    
-   **transferStatisfic(contactFlowId)**
    
    ```
    /**
     * 发送语音满意度,或者转其他IVR流程。
     *
     * @param contactFlowId 如果不传，则发起已配置的语音满意度流程。也可以传入指定IVR流程ID，发起指定IVR流程。发起IVR流程后，当前坐席被挂断。
     */
    transferStatisfic(contactFlowId?: string): void;
    ```
    
-   **launchShortMessageAppraise()**
    
    ```
    发送短信满意度，只有在话后处理状态下可用。
    ```
    
-   **launchShortMessageMissedCall()**
    
    ```
    发送漏话短信，只有在拨号状态时可用。
    ```
    

-   **launchAuthentication(contactFlowId, contactFlowVariables, callback)**
    

```
/**
 * 发送指定IVR流程，当前坐席不被挂断。
 *
 * @param contactFlowId 发起指定IVR流程的ID
 * @param contactFlowVariables 给 IVR 流程传参，可在开始节点中定义同名参数获取
 * @param callback 核身接口调用成功的回调
 */
launchAuthentication(
  contactFlowId: string,
  contactFlowVariables?: Record<string, string | number>,
  callback?: (e: any) => void,
): void;
```

-   **forceToPrepareSignIn()**
    
    ```
     如果注册时收到7001错误，即已有设备在线，可以调用此方法继续注册。成功后会把原有设备踢下线。
    ```
    
-   **testTurnServers(args)**
    
    ```
    测试云呼坐席接入点的时间。args的参数形式为：
    accessPoint: 可以只测某个接入点的值。不传为测试当前所有接入点。
    currentFrequence： 测试几次。不传为1次，参数类型为Number。
    callback: (res) => { 在这里得到接入点结果 }。
    ```
    
-   **switchAccessPoint(accessPoint)**
    
    ```
    切换坐席接入点，accessPoint为从接口GetTurnServerList获取的turnServerListConfig数组对象的region，
    必须和接口region保持一致，否则不能切换成功，自动传“default”。
    ```
    
-   **getSoftPhoneDeviceId()**
    
    ```
    获取当前软电话id。可以根据此值进行MakeCall接口调用。
    ```
    
-   **getAudioDeviceList(callbackFunction)**
    
    ```
    获取当前麦克风和耳机列表。
    ```
    
-   **setAudioInputDevice(device\_id)**
    
    ```
    设置麦克风设备。
    ```
    
-   **setAudioOutputDevice(device\_id)**
    
    ```
    设置耳机设备。
    ```
    
-   **cancelAutomaticCallRelease**
    
    ```
    取消外呼智能挂机设置（“设置-坐席工作台-坐席接听-外呼智能挂机”中配置）的自动挂机操作。
    ```
    
-   **getRemoteMediaStream**
    
    ```
    /**
     * 获取远程媒体流，可以自定义媒体播放
     */
    getRemoteMediaStream(): Promise<MediaStream>;
    ```
    
-   **getSkillGroups**
    
    ```
    /**
     * 获取技能组
     */
    getSkillGroups(): {
      /**
       * 上线时已选择的技能组列表
       */
      chooseSkillGroupList:  ListSkillLevelsOfUser[]
      /**
       * 坐席当前所属技能组列表 （ListSkillLevelsOfUser 接口返回）
       */
      allSkillGroupList:  ListSkillLevelsOfUser[]
    }
    
    interface ListSkillLevelsOfUser {
      /**
       * 技能组ID
       */
      skillGroupId: string;
    
      /**
       * 技能组名称
       */
      skillGroupName: string;
    
      /**
       * 技能组等级
       */
      skillLevel: number;
    }
    ```
    
-   **renderIM**
    
    ```
    IM组件渲染，需要加载对应IM组件的css和js文件。在onLogin及之后的钩子函数中调用。
    ```
    
-   **unmontIM**
    
    ```
    IM组件卸载，需要加载对应IM组件的css和js文件。在onLogOut钩子函数中调用以卸载IM组件。
    ```
    

## 服务端准备工作

因为软电话SDK是嵌入到了您的自有业务系统中，在软电话SDK的使用过程中，会发起多个请求到自有业务系统的服务端，请求的调用地址可以通过**config可选配置**中的**ajax**相关配置来设置。需要将软电话SDK发出的请求经过您的服务端转发到云联络中心的服务端（也就是调用云联络中心的OpenAPI），然后将返回结果透传回软电话SDK中即可。详细步骤如下：

-   可以通过AK/SK方式请求接口，或通过oauth2方式请求接口。
    
-   转发SDK发送的请求到云联络中心服务端，根据[简介](https://help.aliyun.com/zh/document_detail/85054.html)调用对应OpenAPI，将返回结果透传回软电话SDK即可，软电话SDK所需的返回结果必须是JSON数据格式。
    
-   坐席，技能组等需要在云联络中心控制台进行配置，否则无法正常工作。
    

| **类型** | **接口** | **描述** |
| --- | --- | --- |
| **业务接口** | GetLoginDetails | 获取坐席的登录信息。 |
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
| **话务操作相关接口** | SignOutGroup | 退出。 |
| TakeBreak | 小休。 |
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

## 开发错误、操作逻辑错误

SDK会抛出两种类型的错误：开发错误和操作逻辑错误。建议您在开发时配置onErrorNotify钩子并打印参数，方便排查问题并将相关错误抛出给客户以方便问题排查。

1.  开发错误：简单地说就是可以通过修改您的代码来修复的错误，是稳定重现的，这一类型的错误常见的有配置参数类型出错、调用SDK方法未按照状态约束表进行。比如配置项onInit要求是一个方法，但是却传入了一个字符串，那么SDK会直接执行如下代码，遇到这样的错误js执行被打断，必须要根据错误提示先进行修复。
    
2.  操作逻辑错误：这一类错误是用户在使用云联络中心过程中一些操作不当造成的错误，不一定是稳定重现的，这一类型的错误常见的有未允许浏览器对本域名开启声卡权限、账号在别处登录、客服不在任何技能组中、云联络中心网络错误等。这类错误SDK会调用onErrorNotify方法通知外部系统，钩子函数onErrorNotify中的所有情况：
    
    ```
      5001: '外呼失败'。
      5002: '您尚未被加入到技能组中，暂时无法使用，请联系呼叫中心管理员添加'。
      5003: '技能组信息异常'。
      5004: '请检查坐席是否在通话中，并且设置了语音满意度流程'。
      5005: '当前WebSocket连接缓慢，请等待或刷新后重新上线'。
      5006: '请检查坐席是否在通话中，并且传入IVR流程ID'。
      6001: '没有通话Channel信息'。
      6002: '没有通话ChannelID'。
      6010: 'sip会话尚未建立'。
      7001: '已有设备注册，软电话未初始化'。 // 初始化sip之前检测出有设备，可以让客户选择是否登录
      7002: '已有设备注册，软电话初始化异常, 请刷新页面'。 // 初始化sip之后，注册设备和sip不一致，报错
      7003: '无法获取接入点信息'。
      7004: '接入点测速失败'。
      7005: '请使用http协议'。
      7006: '浏览器不满足要求'。
      7007: '现在有新设备上线，请检查'。
      7008: 'SIP话机不在线'。
      9001: '当前状态不能执行此操作'。
      9002: '参数异常'。
      9003: '执行失败'。
      9004: '软电话已初始化好'。
      9005: '请先调用PrepareSignIn方法'。
      9006: '下线失败'。
      9007: '网络连接失败'。
      9008: '缺少登录信息'。
      9009: '主叫为空'。
      9010: '无可用主叫'。
      9012: '被叫为空'。
      8001: '请检查声卡权限'。 // 提示设备异常的界面
      8002: '请检查声卡权限'。 // 提示设备异常的界面
      8003: '已在通话中'。
      8011: '检测到通话网络断开，请检查网络后，重新建立通话'。
      /* 以下为迁出的event事件 */
      stream_local_refused: '浏览器无麦克风权限，请刷新页面'。
      get_lo_failed: '无法获取本地媒体流，请切换接入点到上海'。
      PollUserStatusErrorNotify: '无法获取坐席状态，请重新登录'。
    ```
    

注：

```
7001错误中返回值事例：
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

当收到7001错误时，可调用forceToPrepareSignIn接口继续注册，并把原设备踢出。

```
5001﻿错误中返回的errorMsg是外呼失败所对应的sip code，errorMsgTip是sip code所对应的语义翻译。
不同号码运营商所对应的sip code可能有所差异，这里列出常见sip code关系表：
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

## 状态对照表及状态说明

| **状态码** | **描述** | **操作** | **可允许调用的接口** |
| --- | --- | --- | --- |
| \\-1 | 未注册 | 当前状态只能操作register | register |
| 0   | 注册中 |     | register |
| 1   | 离线  | 上线  | logIn, applyForOffSite, forceToPrepareSignIn |
| 2   | 小休  | 置空闲，仅外呼，下线 | ready, applyForCallOnly, changeVisibility, logOut |
| 3   | 空闲  | 下线、外呼、接听，发起监听，会议 | logOut, agentToAgent, call, monitor, applyForBreak, applyForCallOnly,bargeIn, intercept, coach, startConference |
| 4   | 仅外呼 | 下线、外呼、接听、发起监听、会议、置空闲 | logOut, agentToAgent, call, monitor, applyForBreak,changeVisibility, ready，bargeIn, intercept, coach, startConference |
| 5   | 话后处理 | 置空闲 | logOut, applyForBreak, ready, call, launchShortMessageAppraise, applyForCallOnly, applyForOffSite |
| 6   | 振铃  | 接听  | answer |
| 7   | IM正在工作中 |     |     |
| 8   | 拨号  | 挂断  | hangUp,sendDtmf |
| 9   | 呼入通话 | 挂断  | hangUp, callHold, callRetrieve, sendDtmf, muteAgent, umMuteAgent, transferStatisfic, launchAuthentication, thirdCallTransfer, initiateAttendedTransfer |
| 10  | 呼出通话 | 挂断  | hangUp, callHold, callRetrieve, sendDtmf, muteAgent, umMuteAgent, transferStatisfic, launchAuthentication, thirdCallTransfer, initiateAttendedTransfer |
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

## 多标签页外呼使用要点

### 使用场景

```
做了CRM系统集成的用户，可以使用我们的SDK界面进行外呼，但是也存在一些用户需要在其他页面，比如一些用户名单列表或用户详情页面通过点击按钮进行外呼，这时就需要在该页面进行sdk注册，但是我们的sdk是不支持多标签注册的，因此我们提供了这样的方案：在注册过sdk的标签页监听其他标签页localstorage的变化，在其他标签页设置localstorage来实现外呼。
```

### 使用方法

1.  设置配置项useLocalStorageToCall为true。
    
2.  首先所有标签页都要在一个浏览器中，要求只有一个标签页注册WorkbenchSdk，并保持该标签页的登录状态。
    
3.  在**其他标签页**拨打电话时设置一个localstorage（如果拨打电话页和注册页处于同一标签页，该方法将无法监听到，导致电话拨打不出去），key为workbenchSdkCall，value为{callee: ‘1558888\*\*\*\*’, caller: ‘05712823\*\*\*\*’, random: 0.234234234}。其中caller的值具体设置参照上面SDK方法中`call(callee, caller)`的规定，设置成功以后，当注册过WorkbenchSdk的标签页监听到localstorge的workbenchSdkCall变化时，便自动外呼电话：
    
    ```
    const value = {
      callee: "1558888****",
      caller: "05712823****",
      publicKey: "",
      useVirNumCall: true,
      random: Math.random(),
    };
    localStorage.setItem("workbenchSdkCall", JSON.stringify(value));
    ```
    
4.  在其他标签页挂断电话时，需设置一个key为workbenchSdkHangup，value为一个随机数的localstorage，便自动挂断电话。
    
    ```
     localStorage.setItem('workbenchSdkHangup',  Math.random())
    ```
    
5.  可通过`localStorage.getItem('workbenchSdkStatus')`来查询当前workbench状态码，当值为3，4，5时才可以外拨号码；当值为8，9，10，11，12，21时才可挂断电话。
    

## 对比1.0SDK文档的更新

1.  **前端资源地址有变化。**
    
2.  **config必选配置项：**
    
    -   instanceId数据来源有变化，为呼叫中心填写的唯一域名。
        
    -   新增regionId配置，删除useOpenApiSdk参数。
        
3.  **config可选配置：**
    
    -   前端请求资源的路径配置为：${ajaxOrigin}${ajaxPath}${ajaxApiParamName}=${apiName}&product=CloudCallCenter&version=2020-07-01&region=${regionId}。
        
    -   回调函数onCallComing、onBeforeCallDialing、onCallDialing、onBeforeCallHangup、onCallEstablish、onErrorNotify、onStatusChange返回的参数都统一为对象格式，具体见文档说明。
        
    -   删除enableRecord配置项。
        
4.  **SDK方法：**
    
    -   离线坐席手机功能放到了坐席管理，通过后端接口修改坐席工作模式，不在前端SDK中提供了。
        
5.  **服务端准备工作，新增了话务相关的接口，详见上方文档说明。**
    
6.  **错误的code码：**
    
    -   减少了双登相关的错误码、2.0如果发现有坐席登录，提示已有设备在线，并列出设备id，请坐席确认。
        
7.  **状态说明：**
    
    -   小休状态码变成了2。
        

## 更新日志

### 2024-08-01

**Workbench: 2.16.0** (3.x版本已发布，使用新功能请前往[前端SDK文档接入（3.x）](https://help.aliyun.com/zh/ccs/cccai/use-cases/ccc-sdk-frontend-access-3)升级）。

**Agentbar: 2.4.0**

**Bug Fixes**

-   闪信接口参数调整。
    

### 2024-05-16

**Workbench: 3.0.4 （**Workbench 3.x后不在此文档维护更新内容，请移步 [前端SDK文档接入（3.x）](https://help.aliyun.com/zh/ccs/cccai/use-cases/ccc-sdk-frontend-access-3)，从2.x迁移到3.x，请查看[十二、从2.x版本升级](https://help.aliyun.com/zh/ccs/cccai/use-cases/ccc-sdk-frontend-access-3#dda7673269o0u)**）。**

**Features**

-   界面样式升级，更符合现代化的视觉效果。
    
-   界面支持多种上线方式，正常上线、小休上线和隐身上线。
    
-   新增工单创建、会话小结、语音转文本、AI助手等功能（需要切换到新版云联络中心，目前功能需要加白名单，请钉钉联系cccsupport2开通）。
    
-   新增开发日志调试功能，将SDK中所有的日志支持自定义收集。
    

**Performance Improvements**

-   简化接入流程，优化资源体积，提升系统稳定。
    
-   优化语音业务和网络业务的单独登录。
    
-   优化底层上线逻辑，使上线过程简化，加快上线效率。
    

### 2024-05-15

**Workbench: 2.15.0**

**Agentbar: 2.4.0**

**Features**

-   添加闪信功能，在设置tab页显示闪信功能开关（闪信功能的使用的前提是在坐席工作台的**设置**\>**闪****信配置**中添加闪信供应商）。
    

**IM SDK: 0.5.8**

**Features**

-   新增会话消息引用功能。
    
-   新增发送2分钟内的消息撤回功能。
    
-   新增发送满意度功能。
    

**Performance Improvements**

-   优化上线逻辑和断线重连逻辑。
    

### 2024-03-01

**Workbench: 2.14.1**

**Agentbar: 2.3.1**

**Bug Fixes**

-   修复状态从3-5后，不自动空闲。
    
-   修复浏览器通知点击后聚焦到当前工作页面。
    

**Features**

-   【云呼叫中心】更名为【云联络中心】。
    
-   新增通话记录中可拉黑号码操作，该操作需要在打开【设置-坐席工作台-坐席配置-是否允许坐席拉黑号码】配置。
    
-   漏话短信支持在多条短信模板中选择一个发送。
    
-   添加IM组件，添加`imConfig`配置项，添加`renderIM`和`unmountIM`两个方法（具体使用方式请查看上方文档）。
    
-   新增状态`7`，为IM工作中的状态。
    

### 2024-01-09

**Workbench: 2.13.1**

**Agentbar: 2.2.0**

**Bug Fixes**

-   `onHangUp` 钩子函数添加`internalcall`（内部通话）type类型。
    

**Features**

-   优化`thirdCallTransfer`和`initiateAttendedTransfer`方法的传参方式，添加`strategyName`、`strategyParams`、`timeoutSeconds`参数。
    
-   添加隐藏界面上预测式外呼变量字段，在坐席控制台-设置-坐席工作台配置中设置。
    

### 2023-11-08

**Workbench: 2.12.2**

**Agentbar: 2.1.2**

**Bug Fixes**

-   修复处于场外模式在onInit的时候调用register上线时，并没有以场内模式上线。
    

**Features**

-   新增 `defaultLastSelectedCallerNumber` 配置参数，主叫号码，默认选中上次选择的。
    
-   **仅外呼**名称更改为**隐身**，在除下线状态外的其他状态，都可切换隐身，隐身模式的作用跟仅外呼一致（**数据报表目前还是仅外呼，仅SDK目前做了更改，后续数据报表也会同步更改**）。
    
-   新增业务接口 ChangeVisibility 切换隐身。
    
-   新增 SDK 实例方法 `changeVisibility`主动切换隐身。
    
-   新增 `isLoggedInvisibility` 配置参数，登录后保持隐身。
    
-   `register`方法新增 `mode`和`breakReason`参数，具体可查看`register`方法说明。
    
-   `logIn`方法新增 `mode`和`breakReason`参数，具体可查看`logIn`方法说明。
    

### 2023-09-20

**Workbench: 2.11.0**

**Agentbar: 2.0.3**

**Bug Fixes**

-   修复在SIP WebSocket断线重连时导致通话也被中断。
    

### 2023-08-21

**Workbench: 2.11.0**

**Agentbar: 2.0.2 （从当前版本开始，不需要再加载SIPml资源）**

**Performance Improvements**

-   优化底层sip连接逻辑，去除SIPml js资源加载。
    

### 2023-06-30

**Workbench: 2.11.0**

**Agentbar: 1.15.1**

**SIPml: 0.6.2**

**Bug Fixes**

-   上线时技能组选择不能超过36个，限制保持跟后端一致。
    

**Features**

-   技能组转接时可以选择转接策略。
    
-   添加ice协商失败的错误处理（8011 错误码）。
    

### 2023-05-25

**Workbench: 2.10.1**

**Agentbar: 1.14.4**

**SIPml: 0.6.1**

**Bug Fixes**

-   兼容某些移动端`HTMLMediaElement.setSinkId`方法不存在，导致上线失败的问题。
    
-   在卸载软电话的时候移除Audio元素，修复上下线后设置设备时不生效的问题。
    
-   将`umMuteAgent`改为`unMuteAgent`，`umMuteAgent`仍然可用但是会在后续某个版本会删除。
    

**Features**

-   `changeVolumeInCall`方法，可以将音量设置到0和1。
    
-   新增 `getRemoteMediaStream`方法，可以在通话中获取远程媒体流。
    
-   优化接入点测速逻辑。
    

### 2023-04-11

**Workbench: 2.10.0**

**Agentbar: 1.14.2**

**SIPml: 0.6.1**

**Bug Fixes**

-   修复自动加载日志配置文件，在某些特殊环境中失败的问题（微前端等场景）。
    
-   修复强插操作时，在某些情况下会接听不了的问题。
    
-   优化挂机的sip code和sip msg.
    
-   优化 sip token 过期刷新机制，解决长时间下线状态再上线时失败的问题。
    
-   修复在通话保持时被监听，通话取回失败的问题。
    
-   上线时技能组选择不能超过36个，限制保持跟后端一致。
    
-   优化同浏览器多tab页，多次相互踢登的问题。
    

**Features**

-   转接技能组时添加优先级选择。
    

### 2023-03-21

**Workbench: 2.8.3**

**Agentbar: 1.12.1**

**SIPml: 0.6.0**

**Bug Fixes**

-   修复 onErrorNotify 钩子函数中，errorMsg和errorMsgTip参数传值错误的问题，应该是字符串但是传了对象（该错误在2.7.0版本开始出现，此版本修复）。
    

**Features**

-   优化日志系统，删除不必要的日志记录上传，减少网络带宽。
    

### 2023-02-28

**Workbench: 2.8.1**

**Agentbar: 1.12.0**

**SIPml: 0.5.0**

**Features**

-   拨打未接通原因sipCode详情展示。
    

### 2022-12-13

**Workbench: 2.8.0**

**Agentbar: 1.12.0**

**SIPml: 0.5.0**

**Features**

-   新增外呼智能挂机功能，可在云呼控制台“设置-坐席工作台-坐席接听-外呼智能挂机”中开启，开启后根据设置的时间倒计时后自动挂机，振铃音智能识别出来的信息在`5001`错误的 `errorMsgTip`字段中返回，`onAfterEarlyMediaRecognized`钩子方法得到早媒体信息，`cancelAutomaticCallRelease`手动取消自动挂机。
    
-   新增自定义通话保持音乐，可在云呼控制台“设置-坐席工作台-坐席接听-通话保持音乐”中设置。
    
-   在小休状态也可以调用`applyForCallOnly`方法。
    

**Performance Improvements**

-   优化 reRender 方法，避免在部分情况下导致旧的挂载组件仍然存在。
    

### 2022-11-18

**Workbench: 2.7.0**

**Agentbar: 1.11.0**

**SIPml: 0.5.0**

**Bug Fixes**

-   后台自动签出，前端再次上线时报9004。
    
-   中文用户名注册失败。
    

**Features**

-   添加允许拒接来电操作，云呼叫中心控制台“设置-坐席工作台-坐席接听”中设置“允许拒接来电”
    
-   优化部分API请求报错的错误提示。
    

**Performance Improvements**

-   项目整体体积减小，提升加载效率。
    

### 2022-10-10

**Workbench: 2.6.1**

**Agentbar: 1.10.0**

**SIPml: 0.5.0**

**Bug Fixes**

-   在话后处理时，切换tab导致通话时间丢失。
    

**Features**

-   在面板中操作小休，添加小休状态选择，可在云呼叫中心控制台“设置-坐席工作台-坐席配置”中设置“小休状态细分配置”。
    
-   切换场外模式时，可进行技能组的选择。
    

**Performance Improvements**

-   选号逻辑提供降级机制，当自动选号接口失败时，开启随机选择号码，不影响拨打操作。
    
-   AnswerCall接口增加容错能力，AnswerCall和Sip接听解耦，在非SIP话机模式登录时，AnswerCall接口调用失败，不影响客户的接听操作。
    

### 2022-08-31

**Workbench: 2.5.0**

**Agentbar: 1.9.0**

**SIPml: 0.5.0**

**Features**

-   添加 `changeRingToneVolume`方法，改变来电响铃的音量。
    
-   咨询通话的时候增加拨号盘功能。
    
-   样式优化，部分地方显示异常修复。
    

**BreakingChanges**

-   当在云呼叫中心控制台“设置-坐席工作台-坐席接听”中设置了外呼或来电号码隐藏时，**为了数据安全考虑，坐席权限的用户，后端接口返回的是脱敏号码**，通话记录中点击拨打按钮会调用 RedialCall 接口，不再调用MakeCall接口，请尽快升级到此版本或以上版本，未升级的用户可能出现拨打失败的情况。
    

### 2022-07-27

**Workbench: 2.4.4**

**Agentbar: 1.8.1**

**SIPml: 0.4.1**

**Bug Fixes**

-   切换左侧导航栏导致呼出tab选中的主叫号码不显示。
    

**Features**

-   添加`onSelectCurrentCallRecord`钩子函数，在通话记录中点击返回当前点击的通话记录信息。
    
-   添加`isOutboundNotReceivedToBeProcessed`配置参数，可使呼出电话且未接通可以到话后处理倒计时状态。
    
-   添加`stayAfterCall`实例方法，保持话后处理状态（与通话结束，点击话后处理按钮效果一致）。
    
-   优化 `unloadWorkbench`卸载实例方法。
    

### 2022-06-29

**Workbench: 2.4.3**

**Agentbar: 1.8.1**

**SIPml: 0.4.0**

**Bug Fixes**

-   呼入通话，咨询转接外部通话后转移通话，咨询者报错问题修复。
    

### 2022-06-28

**Workbench: 2.4**.**2**

**Agentbar: 1.8.1**

**SIPml: 0.4.0**

**Bug Fixes**

-   优化浏览器版本判断逻辑。
    
-   修复在某些情况下不刷新页面更换用户登录，钩子函数不触发的问题。
    

**Features**

-   添加`isLoggedKeepBreak`配置参数，登录时保持小休状态。
    

### 2022-06-21

**Workbench: 2.4.1**

**Agentbar: 1.8.0**

**SIPml: 0.4.0**

**Bug Fixes**

-   来电技能组太长显示tooltip。
    
-   修复切换场外模式再立马以场内模式上线参数没有更新的问题。
    
-   部分通话时间累计问题修复。
    
-   修复 moreActionList 填写不支持的参数报错。
    
-   修复面板收起时主被叫号码更新不及时。
    
-   收缩盘样式的更改，兼容被叫号码超长的逻辑。
    
-   修复咨询通话-转移通话时，被叫归属地未显示，呼入时主叫来电次数和来电时间未显示。
    
-   修复IVRTracking中，有设置变量节点时报错。
    
-   修复设备检测，麦克风和耳机选择设备选择框中不显示。
    
-   修复呼入出现滚动条，状态图标被覆盖。
    
-   register方法传deviceType参数为0时，弹窗还是出现。
    
-   缩小面板后，点击接听按钮，传参错误。
    
-   修复获取浏览器版本号逻辑，兼容chrom 100版本。
    
-   优化界面显示，提升体验。
    

**Features**

-   `launchAuthentication`核身方法添加 `contactFlowVariables`变量和 `callback`成功回调方法。
    
-   `sendDtmf`方法开放出 `jobId`和 `channelId`参数传入。
    
-   发送语音满意度添加loading状态。
    
-   来电呼入页面中添加来电技能组字段显示。
    
-   添加仅外呼配置。
    
-   添加仅外呼状态是否可以接收任何来电配置，转接和内部通话是否可以给坐席。
    
-   SIPml 添加更多日志，方便排查问题。
    

**Performance Improvements**

-   优化 agentbar 体积，js文件减小55%，提升加载效率。