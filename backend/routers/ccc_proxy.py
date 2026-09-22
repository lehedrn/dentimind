"""
CCC API 通用代理接口

把前端 Workbench SDK 发来的请求转发到阿里云 CCC OpenAPI。
使用动态分发：根据 action 参数找到对应的 Request 类和 Client 方法，
避免为每个 API 单独写代码。
"""
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from alibabacloud_ccc20200701 import models
from services.aliyun_ccc import CCCService
import inspect
import re
import os
import logging
import json
from typing import Any, Dict

logger = logging.getLogger(__name__)

router = APIRouter(tags=["CCC Proxy"])

# 复用现有 CCC 服务实例（带 client 和认证）
_ccc_service = CCCService()
_client = _ccc_service.client
_instance_id = _ccc_service.instance_id

# 预缓存每个 Request 类接受的参数名（避免每次 inspect）
_param_cache: Dict[type, set] = {}


def _get_accepted_params(request_class: type) -> set:
    """获取 Request 类的 __init__ 接受的有效参数名"""
    if request_class not in _param_cache:
        sig = inspect.signature(request_class.__init__)
        params = {name for name in sig.parameters if name != "self"}
        _param_cache[request_class] = params
    return _param_cache[request_class]


def _pascal_to_snake(name: str) -> str:
    """PascalCase/camelCase → snake_case
    例：InstanceId → instance_id, callId → call_id
    """
    # 先处理连续大写：HTTPRequest → http_request
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    # 再处理普通驼峰：instanceId → instance_Id
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def _snake_to_camel(name: str) -> str:
    """snake_case → camelCase
    例：instance_id → instanceId
    """
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _pascal_to_camel(name: str) -> str:
    """PascalCase → camelCase
    例：SkillGroupId → skillGroupId, PageNumber → pageNumber
    """
    if not name:
        return name
    # 如果已经是 camelCase（首字母小写），直接返回
    if name[0].islower():
        return name
    # 否则将首字母转为小写
    return name[0].lower() + name[1:]


def _pascal_to_camel(name: str) -> str:
    """PascalCase → camelCase"""
    if not name:
        return name
    if name[0].islower():
        return name
    return name[0].lower() + name[1:]


def _transform_response_value(value: Any) -> Any:
    """递归转换响应值为 JSON 可序列化格式，字段名转为 camelCase"""
    if value is None:
        return None
    if hasattr(value, "to_map"):
        return _transform_response_value(value.to_map())
    if isinstance(value, dict):
        return {_pascal_to_camel(k): _transform_response_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_transform_response_value(item) for item in value]
    return value


def _format_response(response, action: str = "") -> dict:
    """将 CCC SDK 响应对象转换为前端 SDK 期望的格式
    {code, data, httpStatusCode, requestId}
    """
    body = getattr(response, "body", response)

    # 提取核心字段（兼容 snake_case 和 PascalCase）
    code = (
        getattr(body, "code", None) or
        getattr(body, "Code", None)
    )
    data = getattr(body, "data", None) or getattr(body, "Data", None)
    http_status = (
        getattr(body, "http_status_code", None) or
        getattr(body, "httpStatusCode", None) or
        getattr(body, "HttpStatusCode", None)
    )
    request_id = (
        getattr(body, "request_id", None) or
        getattr(body, "requestId", None) or
        getattr(body, "RequestId", None)
    )
    message = (
        getattr(body, "message", None) or
        getattr(body, "Message", None)
    )

    # 如果 body 有 to_map 方法，用它获取完整数据
    if data is None and hasattr(body, "to_map"):
        body_map = body.to_map()
        # 排除元数据字段，剩下的都算 data
        meta_keys = {"Code", "code", "HttpStatusCode", "httpStatusCode",
                     "RequestId", "requestId", "Message", "message"}
        data = {k: v for k, v in body_map.items() if k not in meta_keys}
        if not data:
            data = body_map

    # 特殊处理：为 ListSkillLevelsOfUser 的技能组添加 MediaType（在转换前，用 PascalCase）
    if action == "ListSkillLevelsOfUser" and isinstance(data, dict):
        skill_list = data.get("List", [])
        for skill in skill_list:
            if "MediaType" not in skill:
                skill_id = skill.get("SkillGroupId", "")
                if "chat" in skill_id.lower() or "im" in skill_id.lower():
                    skill["MediaType"] = "CHAT"
                else:
                    skill["MediaType"] = "AUDIO"

    # 特殊处理：ListDevices - CCC API 返回 Data.Data 嵌套结构，需要解包
    if action == "ListDevices" and isinstance(data, dict):
        inner = data.get("Data", data.get("data", None))
        if isinstance(inner, list):
            data = inner
            logger.info(f"ListDevices 解包嵌套 Data: {len(data)} 个设备")

    # 特殊处理：ListDevices - 为设备添加 SDK 需要的 Status 字段（PascalCase）
    if action == "ListDevices" and isinstance(data, list):
        import time
        enriched_devices = []
        for device in data:
            if hasattr(device, "to_map"):
                device_dict = device.to_map()
            elif isinstance(device, dict):
                device_dict = device
            else:
                continue

            # 根据 expires 判断状态（使用 PascalCase）
            expires = device_dict.get("Expires", 0)
            if expires > time.time() * 1000:
                device_dict["Status"] = "Online"
            else:
                device_dict["Status"] = "Offline"

            # 添加 Type 和 MediaType（PascalCase，纯语音模式）
            if "Type" not in device_dict:
                device_dict["Type"] = "Voice"
            if "MediaType" not in device_dict:
                device_dict["MediaType"] = "Voice"

            enriched_devices.append(device_dict)

        data = enriched_devices
        logger.info(f"ListDevices 补充状态后: {len(data)} 个设备")

    # 将 CCC SDK 对象转换为字典（保持 PascalCase）
    def _to_dict_pascal_case(value):
        """递归转换值为字典，保持 PascalCase 字段名"""
        if value is None:
            return None
        if hasattr(value, "to_map"):
            return _to_dict_pascal_case(value.to_map())
        if isinstance(value, dict):
            return {k: _to_dict_pascal_case(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [_to_dict_pascal_case(item) for item in value]
        return value

    data = _to_dict_pascal_case(data)

    # 2.x SDK 期望阿里云 API 的原始格式（PascalCase）
    result = {
        "Code": code or "OK",
        "Data": data,
        "HttpStatusCode": http_status or 200,
        "RequestId": request_id or "",
    }
    if message:
        result["Message"] = message

    return result


async def _parse_request_params(request: Request) -> Dict[str, Any]:
    """从请求中提取所有参数（query + body，body 优先）"""
    params = dict(request.query_params)

    content_type = request.headers.get("content-type", "")
    try:
        if "application/json" in content_type:
            try:
                body = await request.json()
                if isinstance(body, dict):
                    # 扁平化：如果 body 中有 params 嵌套，展开它
                    params.update(body)
            except Exception:
                pass
        elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            form = await request.form()
            params.update(dict(form))
        else:
            # 尝试作为 JSON 或 form 解析
            try:
                body = await request.json()
                if isinstance(body, dict):
                    params.update(body)
            except Exception:
                try:
                    form = await request.form()
                    params.update(dict(form))
                except Exception:
                    pass
    except Exception as e:
        logger.warning(f"解析请求体失败: {e}")

    # 解析 request 字段中的 JSON 参数（SDK 2.x 格式）
    if "request" in params and isinstance(params["request"], str):
        try:
            request_json = json.loads(params["request"])
            if isinstance(request_json, dict):
                # 将 request 中的参数合并到 params 中（request 中的参数优先）
                for key, value in request_json.items():
                    params[key] = value
                logger.info(f"解析 request JSON: {list(request_json.keys())}")
        except Exception as e:
            logger.warning(f"解析 request JSON 失败: {e}")

    return params


# ====== 代理端点 ======

@router.api_route(
    "/api/ccc-proxy",
    methods=["GET", "POST"],
    summary="CCC OpenAPI 通用代理",
)
@router.api_route(
    "/data/api.json",  # SDK 默认 ajaxPath
    methods=["GET", "POST"],
    include_in_schema=False,
)
async def ccc_proxy(request: Request):
    """
    代理前端 Workbench SDK 的请求到阿里云 CCC OpenAPI。

    请求示例:
        POST /api/ccc-proxy?action=GetAgentState&InstanceId=demo-xxx&UserId=xxx

    返回格式:
        {"code": "OK", "data": {...}, "httpStatusCode": 200, "requestId": "xxx"}
    """
    if not _client:
        return JSONResponse(
            status_code=503,
            content={
                "code": "ServiceUnavailable",
                "message": "CCC 服务未初始化，请检查 AK/SK 配置",
                "httpStatusCode": 503,
            },
        )

    try:
        # 1. 解析参数
        params = await _parse_request_params(request)
        action = params.pop("action", None) or params.pop("Action", None)

        if not action:
            return JSONResponse(
                status_code=400,
                content={
                    "code": "MissingAction",
                    "message": "缺少 action 参数",
                    "httpStatusCode": 400,
                },
            )

        # 详细日志：请求参数
        logger.info(f"\n{'='*80}")
        logger.info(f"🔵 SDK 请求: {action}")
        logger.info(f"📋 参数: {params if params else {}}")
        logger.info(f"{'='*80}")

        # 2. 查找 Request 类和 Client 方法
        request_class_name = f"{action}Request"
        request_class = getattr(models, request_class_name, None)
        if request_class is None:
            logger.warning(f"未知的 CCC API: {action} (类 {request_class_name} 不存在)")
            return JSONResponse(
                status_code=400,
                content={
                    "code": "UnknownAction",
                    "message": f"不支持的 action: {action}",
                    "httpStatusCode": 400,
                },
            )

        method_name = _pascal_to_snake(action)
        client_method = getattr(_client, method_name, None)
        if client_method is None:
            logger.warning(f"Client 缺少方法: {method_name}")
            return JSONResponse(
                status_code=500,
                content={
                    "code": "InternalError",
                    "message": f"CCC Client 缺少方法: {method_name}",
                    "httpStatusCode": 500,
                },
            )

        # 3. 构造请求对象（过滤无效参数，转换命名风格，注入默认值）
        accepted = _get_accepted_params(request_class)
        kwargs = {}

        for key, value in params.items():
            # 跳过空值（空字符串、None、"null"、"undefined"）
            if value is None:
                continue
            if isinstance(value, str) and value.strip() in ("", "null", "undefined"):
                continue

            # 尝试直接匹配 snake_case
            snake_key = _pascal_to_snake(key)

            if snake_key in accepted:
                kwargs[snake_key] = value
            elif key in accepted:
                kwargs[key] = value
            # 否则忽略（避免 unexpected keyword argument 错误）

        # 默认注入 instance_id（如果请求没带且 SDK 接受）
        if "instance_id" in accepted and "instance_id" not in kwargs:
            kwargs["instance_id"] = _instance_id

        # 默认注入 user_id（从环境变量或从 instance_id 推导）
        if "user_id" in accepted and "user_id" not in kwargs:
            default_user_id = os.getenv("CCC_USER_ID")
            if default_user_id:
                kwargs["user_id"] = default_user_id

        # 分页参数默认值（SDK 经常不传，但 API 要求必须传）
        if "page_number" in accepted and "page_number" not in kwargs:
            kwargs["page_number"] = 1
        if "page_size" in accepted and "page_size" not in kwargs:
            kwargs["page_size"] = 10

        # device_id 默认值
        if "device_id" in accepted and "device_id" not in kwargs:
            default_device_id = os.getenv("CCC_DEVICE_ID")
            if default_device_id:
                kwargs["device_id"] = default_device_id

        # object_id/object_type 默认值（ListConfigItems 等需要）
        if "object_id" in accepted and "object_id" not in kwargs:
            default_user_id = os.getenv("CCC_USER_ID")
            if default_user_id:
                kwargs["object_id"] = default_user_id
        if "object_type" in accepted and "object_type" not in kwargs:
            kwargs["object_type"] = "User"

        # call_id 可选参数（SaveTerminalLog 等，没有就跳过该 API）
        if "call_id" in accepted and "call_id" not in kwargs:
            # 可选日志 API，没有 call_id 时跳过
            if action == "SaveTerminalLog":
                return JSONResponse(
                    status_code=200,
                    content={
                        "code": "OK",
                        "httpStatusCode": 200,
                        "requestId": "",
                        "message": "skipped: no call_id",
                    },
                )

        # SignInGroup 需要 signed_skill_group_id_list 和 chat_device_id
        # CCC API 要求该参数为 JSON 数组字符串（不是 Python 列表）
        if action == "SignInGroup":
            ssgl_key = "signed_skill_group_id_list"
            if ssgl_key in kwargs and isinstance(kwargs[ssgl_key], list):
                import json
                kwargs[ssgl_key] = json.dumps(kwargs[ssgl_key], separators=(",", ":"))
            elif ssgl_key not in kwargs:
                # SDK 没传，自动从 ListSkillLevelsOfUser 获取
                try:
                    list_req = models.ListSkillLevelsOfUserRequest(
                        instance_id=_instance_id,
                        user_id=os.getenv("CCC_USER_ID"),
                        page_number=1,
                        page_size=100,
                    )
                    list_resp = _client.list_skill_levels_of_user(list_req)
                    list_data = list_resp.body.data
                    if list_data and hasattr(list_data, "list"):
                        skill_group_ids = [
                            item.skill_group_id
                            for item in list_data.list
                            if hasattr(item, "skill_group_id")
                        ]
                        if skill_group_ids:
                            import json
                            kwargs[ssgl_key] = json.dumps(skill_group_ids, separators=(",", ":"))
                            logger.info(f"SignInGroup 自动注入技能组: {skill_group_ids}")
                except Exception as e:
                    logger.warning(f"获取技能组列表失败: {e}")

            # 纯语音模式也需要 chat_device_id（即使不使用 IM）
            # 使用与 device_id 相同的值（在参数转换完成后）
            if "chat_device_id" in accepted and "chat_device_id" not in kwargs:
                # 优先使用 device_id，如果没有则使用环境变量
                chat_device_id = kwargs.get("device_id")
                if not chat_device_id:
                    chat_device_id = os.getenv("CCC_DEVICE_ID", "device")
                kwargs["chat_device_id"] = chat_device_id
                logger.info(f"SignInGroup 自动注入 chat_device_id: {chat_device_id}")

        logger.info(f"代理 CCC API: {action}, 参数: {list(kwargs.keys())}")

        # 显式处理 chat_device_id（CCC API 不允许 null 或空字符串）
        if "chat_device_id" in kwargs:
            val = kwargs["chat_device_id"]
            if not val or (isinstance(val, str) and val.strip() in ("", "null", "undefined")):
                # 给一个非空默认值，避免 CCC API 拒绝
                kwargs["chat_device_id"] = os.getenv("CCC_DEVICE_ID", "device")
                logger.info(f"chat_device_id 为空，使用默认值: {kwargs['chat_device_id']}")
# DISABLED:         elif "chat_device_id" in accepted:
# DISABLED:             # Request 类有该字段但 SDK 没传，也设置默认值
# DISABLED:             kwargs["chat_device_id"] = os.getenv("CCC_DEVICE_ID", "device")

        # 4. 调用 CCC API（SignInGroup 支持自动重试）
        request_obj = request_class(**kwargs)

        # CCC SDK 是同步的，放线程池避免阻塞
        import asyncio
        loop = asyncio.get_event_loop()

        # SignInGroup 如果遇到设备状态问题，自动重试
        max_retries = 3 if action == "SignInGroup" else 1
        last_error = None

        for attempt in range(max_retries):
            try:
                response = await loop.run_in_executor(None, client_method, request_obj)

                # 检查响应是否成功
                result = _format_response(response, action)
                result_code = result.get('Code', '') or result.get('code', '')

                # 如果是设备状态问题，等待后重试（首次 10 秒，后续递增）
                if action == "SignInGroup" and result_code == "InvalidOperation.DeviceState":
                    if attempt < max_retries - 1:
                        wait_time = 10 + (attempt * 5)  # 10秒, 15秒
                        logger.warning(f"SignInGroup 设备状态未同步，{wait_time}秒后重试 (尝试 {attempt + 1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        # 所有重试都失败，尝试注销旧设备
                        logger.error(f"SignInGroup 重试 {max_retries} 次后仍然失败，尝试注销旧设备...")
                        try:
                            # 调用 UnregisterDevice API
                            unregister_req = models.UnregisterDeviceRequest(
                                instance_id=_instance_id,
                                user_id=os.getenv("CCC_USER_ID")
                            )
                            await loop.run_in_executor(None, _client.unregister_device, unregister_req)
                            logger.info("✅ 旧设备已注销，请刷新页面重新注册")
                            # 返回特殊响应，告诉前端需要重新注册
                            return JSONResponse(content={
                                "code": "DeviceUnregistered",
                                "message": "旧设备已注销，请刷新页面重新注册",
                                "httpStatusCode": 200,
                                "requestId": "",
                            })
                        except Exception as unregister_err:
                            logger.error(f"注销设备失败: {unregister_err}")

                # 详细日志：响应数据
                logger.info(f"\n{'='*80}")
                logger.info(f"✅ CCC 响应: {action}")
                logger.info(f"📊 响应码: {result_code}")
                logger.info(f"📦 响应数据: {result}")
                logger.info(f"{'='*80}\n")

                logger.info(f"CCC API {action} 响应: code={result_code}")
                return JSONResponse(content=result)

            except Exception as e:
                last_error = e
                # 如果是设备状态相关的异常，等待后重试
                if action == "SignInGroup" and "DeviceState" in str(e) and attempt < max_retries - 1:
                    logger.warning(f"SignInGroup 异常，2秒后重试: {e} (尝试 {attempt + 1}/{max_retries})")
                    await asyncio.sleep(2)
                    continue
                raise

        # 所有重试都失败
        raise last_error

    except Exception as e:
        logger.error(f"代理 CCC API 失败: {action if 'action' in dir() else 'unknown'} - {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "code": "ProxyError",
                "message": f"代理调用失败: {str(e)}",
                "httpStatusCode": 500,
            },
        )


@router.post("/api/ccc-proxy/unregister-device")
async def unregister_device():
    """
    注销当前设备（用于解决设备冲突问题）
    """
    try:
        import asyncio
        loop = asyncio.get_event_loop()

        unregister_req = models.UnregisterDeviceRequest(
            instance_id=_instance_id,
            user_id=os.getenv("CCC_USER_ID")
        )
        await loop.run_in_executor(None, _client.unregister_device, unregister_req)
        logger.info("✅ 设备已注销")

        return JSONResponse(content={
            "success": True,
            "message": "设备已注销",
        })
    except Exception as e:
        logger.error(f"注销设备失败: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"注销设备失败: {str(e)}",
            }
        )


@router.get("/api/ccc-proxy/health")
async def proxy_health():
    """代理接口健康检查"""
    return {
        "status": "ok",
        "service": "ccc-proxy",
        "ccc_configured": _client is not None,
        "instance_id": _instance_id,
    }
