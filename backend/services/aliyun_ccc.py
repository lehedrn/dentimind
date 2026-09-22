"""
阿里云CCC电话服务
封装阿里云CCC OpenAPI调用
"""
import os
import logging
import asyncio
from typing import List, Optional
from alibabacloud_ccc20200701.client import Client
from alibabacloud_ccc20200701 import models
from alibabacloud_tea_openapi.models import Config

logger = logging.getLogger(__name__)


class CCCService:
    """阿里云CCC电话服务"""

    def __init__(self):
        access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
        access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
        region_id = os.getenv("CCC_REGION_ID", "cn-shanghai")

        if not access_key_id or not access_key_secret:
            logger.warning("CCC API配置缺失，电话功能将不可用")
            self.client = None
            self.instance_id = None
            return

        try:
            config = Config(
                access_key_id=access_key_id,
                access_key_secret=access_key_secret,
                endpoint=f"ccc.{region_id}.aliyuncs.com"
            )
            self.client = Client(config)
            self.instance_id = os.getenv("CCC_INSTANCE_ID")
            logger.info(f"CCC服务初始化成功 - instance_id: {self.instance_id}")
        except Exception as e:
            logger.error(f"CCC服务初始化失败: {str(e)}")
            self.client = None
            self.instance_id = None

    async def check_agent_status(self) -> dict:
        """
        检查坐席状态

        Returns:
            {
                "agent_status": "Online" | "Offline" | "Ready" | "NotReady",
                "is_online": True/False,
                "user_id": "坐席ID"
            }
        """
        if not self.client:
            raise Exception("CCC服务未初始化")

        user_id = os.getenv("CCC_USER_ID")
        device_id = os.getenv("CCC_DEVICE_ID", "device")

        logger.info(f"检查坐席状态 - user_id: {user_id}")

        try:
            # 使用 ListRealtimeAgentStatesRequest 获取坐席状态
            request = models.ListRealtimeAgentStatesRequest(
                instance_id=self.instance_id,
                user_id_list=[user_id]
            )

            response = self.client.list_realtime_agent_states(request)

            # 解析响应
            if response.body and response.body.data and response.body.data.list:
                # 找到当前用户的状态
                agent_state = None
                for state_item in response.body.data.list:
                    if hasattr(state_item, 'user_id') and state_item.user_id == user_id:
                        agent_state = state_item
                        break

                if agent_state:
                    state = agent_state.state if hasattr(agent_state, 'state') else 'Unknown'
                    is_online = state in ['Online', 'Ready', 'NotReady', 'Break']

                    result = {
                        "agent_status": state,
                        "is_online": is_online,
                        "user_id": user_id,
                        "device_id": device_id
                    }

                    logger.info(f"坐席状态检查完成 - state: {state}, is_online: {is_online}")
                    return result

            # 没有找到状态信息
            logger.warning(f"未找到坐席状态信息 - user_id: {user_id}")
            return {
                "agent_status": "Unknown",
                "is_online": False,
                "user_id": user_id,
                "error": "Agent state not found"
            }

        except Exception as e:
            logger.error(f"检查坐席状态失败: {str(e)}")
            # 如果查询失败，假设不在线
            return {
                "agent_status": "Unknown",
                "is_online": False,
                "user_id": user_id,
                "error": str(e)
            }

    async def list_skill_groups(self) -> list:
        """
        获取技能组列表

        Returns:
            技能组列表，每个元素包含 skill_group_id 和 name
        """
        if not self.client:
            raise Exception("CCC服务未初始化")

        try:
            request = models.ListSkillGroupsRequest(
                instance_id=self.instance_id,
                page_number=1,
                page_size=100
            )

            response = self.client.list_skill_groups(request)

            skill_groups = []
            if response.body and response.body.data and response.body.data.list:
                for group in response.body.data.list:
                    skill_groups.append({
                        'skill_group_id': group.skill_group_id,
                        'name': group.name if hasattr(group, 'name') else ''
                    })

            logger.info(f"获取到 {len(skill_groups)} 个技能组")
            return skill_groups

        except Exception as e:
            logger.error(f"获取技能组列表失败: {str(e)}")
            return []

    async def sign_in_agent(self) -> dict:
        """
        签到坐席（使坐席上线）

        Returns:
            {
                "success": True/False,
                "message": "签到结果信息"
            }
        """
        if not self.client:
            raise Exception("CCC服务未初始化")

        user_id = os.getenv("CCC_USER_ID")
        device_id = os.getenv("CCC_DEVICE_ID", "device")

        logger.info(f"签到坐席 - user_id: {user_id}, device_id: {device_id}")

        try:
            # 只使用 skg-default 技能组
            skill_group_ids = [f"skg-default@{self.instance_id}"]
            logger.info(f"将签到技能组: {skill_group_ids}")

            # CCC API 要求 signed_skill_group_id_list 为 JSON 字符串格式
            import json
            skill_group_ids_json = json.dumps(skill_group_ids, separators=(",", ":"))
            logger.info(f"技能组ID列表(JSON): {skill_group_ids_json}")

            # 签入坐席，传入技能组ID列表（JSON字符串格式）
            request = models.SignInGroupRequest(
                instance_id=self.instance_id,
                user_id=user_id,
                device_id=device_id,
                signed_skill_group_id_list=skill_group_ids_json
            )

            response = self.client.sign_in_group(request)

            logger.info(f"坐席签到响应: {response.body}")

            # 检查响应是否成功
            if hasattr(response.body, 'code') and response.body.code != 'OK':
                error_msg = f"签到失败: {response.body.message if hasattr(response.body, 'message') else 'Unknown error'}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "message": error_msg,
                    "error": response.body.code if hasattr(response.body, 'code') else 'Unknown'
                }

            result = {
                "success": True,
                "message": "坐席签到成功",
                "user_id": user_id,
                "skill_groups": skill_group_ids
            }

            logger.info(f"坐席签到成功 - user_id: {user_id}, skill_groups: {skill_group_ids}")
            return result

        except Exception as e:
            logger.error(f"坐席签到失败: {str(e)}")
            return {
                "success": False,
                "message": f"坐席签到失败: {str(e)}",
                "error": str(e)
            }

    async def ensure_agent_online(self, auto_sign_in: bool = True) -> dict:
        """
        确保坐席在线

        Args:
            auto_sign_in: 如果不在线，是否自动签到

        Returns:
            {
                "is_online": True/False,
                "agent_status": "坐席状态",
                "action_taken": "采取的操作",
                "success": True/False
            }
        """
        # 检查坐席状态
        status = await self.check_agent_status()

        if status["is_online"]:
            logger.info(f"坐席已在线 - status: {status['agent_status']}")
            return {
                "is_online": True,
                "agent_status": status["agent_status"],
                "action_taken": "none",
                "success": True
            }

        # 坐席不在线
        logger.warning(f"坐席不在线 - status: {status['agent_status']}")

        if not auto_sign_in:
            return {
                "is_online": False,
                "agent_status": status["agent_status"],
                "action_taken": "none",
                "success": False,
                "message": "坐席不在线，需要手动签到"
            }

        # 自动签到
        logger.info("坐席不在线，尝试自动签到...")
        sign_in_result = await self.sign_in_agent()

        if sign_in_result["success"]:
            # 签到后再次检查状态
            await asyncio.sleep(1)  # 等待1秒让签到生效
            new_status = await self.check_agent_status()

            return {
                "is_online": new_status["is_online"],
                "agent_status": new_status["agent_status"],
                "action_taken": "auto_sign_in",
                "success": new_status["is_online"],
                "message": "坐席已自动签到"
            }
        else:
            return {
                "is_online": False,
                "agent_status": status["agent_status"],
                "action_taken": "auto_sign_in_failed",
                "success": False,
                "message": sign_in_result["message"]
            }

    async def make_call(self, callee_number: str, auto_sign_in: bool = False) -> dict:
        """
        发起外呼

        Args:
            callee_number: 被叫号码（手机号）
            auto_sign_in: 是否尝试自动签到（默认False，需要先在软电话登录）

        Returns:
            {
                "call_id": "通话ID",
                "status": "initiated",
                "agent_status": "坐席状态信息"
            }
        """
        if not self.client:
            raise Exception("CCC服务未初始化")

        # 注意：前端已检查坐席状态，后端不再强制检查
        # 如果坐席不在线，CCC API 会返回错误
        logger.info(f"发起外呼 - callee: {callee_number}")

        caller_number = os.getenv("CCC_CALLER_NUMBER")
        user_id = os.getenv("CCC_USER_ID", caller_number)
        device_id = os.getenv("CCC_DEVICE_ID", "device")

        logger.info(f"发起外呼 - caller: {caller_number}, callee: {callee_number}, user_id: {user_id}, device_id: {device_id}")

        try:
            # 使用正确的参数名称
            request = models.MakeCallRequest(
                instance_id=self.instance_id,
                callee=callee_number,
                caller=caller_number,
                user_id=user_id,
                device_id=device_id
            )

            response = self.client.make_call(request)

            # 打印响应结构以便调试
            logger.info(f"CCC响应: {response.body}")

            # 提取 job_id 和 channel_id
            # CCC SDK 响应可能是 snake_case (data.call_context.job_id)
            # 或 PascalCase (Data.CallContext.JobId)，取决于 SDK 版本
            # 必须健壮处理两种情况，并在都失败时用正则提取
            job_id = None
            channel_id = None

            body = response.body

            # 1. 尝试 snake_case 路径
            try:
                data = getattr(body, "data", None) or getattr(body, "Data", None)
                if data:
                    ctx = getattr(data, "call_context", None) or getattr(data, "CallContext", None)
                    if ctx:
                        job_id = (
                            getattr(ctx, "job_id", None)
                            or getattr(ctx, "JobId", None)
                        )
                        channels = (
                            getattr(ctx, "channel_contexts", None)
                            or getattr(ctx, "ChannelContexts", None)
                        )
                        if channels:
                            for ch in channels:
                                cid = getattr(ch, "channel_id", None) or getattr(ch, "ChannelId", None)
                                if cid:
                                    channel_id = cid
                                    break
            except Exception as attr_err:
                logger.warning(f"属性提取失败，回退到字符串解析: {attr_err}")

            # 2. 字符串回退：用正则从 str(response.body) 提取
            if not job_id:
                import re
                body_str = str(body)
                m = re.search(r"[Jj]ob[Ii]d['\":\s=]+([A-Za-z0-9_\-]+)", body_str)
                if m:
                    job_id = m.group(1)
                    logger.info(f"从字符串中提取到 job_id: {job_id}")
                else:
                    logger.warning(f"无法从响应中提取 job_id，使用 response_id 代替")
                    # 最后兜底：用 RequestId 或 UUID，绝不存整个响应体
                    rid = getattr(body, "request_id", None) or getattr(body, "RequestId", None)
                    job_id = rid or f"call-{uuid.uuid4().hex[:12]}"

            call_id = job_id

            result = {
                "call_id": call_id,
                "contact_id": channel_id,
                "job_id": job_id,
                "channel_id": channel_id,
                "status": "initiated",
                "success": True
            }

            logger.info(f"外呼成功 - call_id: {call_id}, contact_id: {channel_id}")
            return result

        except Exception as e:
            logger.error(f"外呼失败: {str(e)}")
            raise

    async def list_call_records(
        self,
        start_time: int,
        end_time: int,
        page_number: int = 1,
        page_size: int = 50
    ) -> list:
        """
        查询通话记录

        Args:
            start_time: 开始时间（Unix时间戳，毫秒）
            end_time: 结束时间（Unix时间戳，毫秒）
            page_number: 页码
            page_size: 每页数量

        Returns:
            通话记录列表
        """
        if not self.client:
            raise Exception("CCC服务未初始化")

        logger.info(f"查询通话记录 - start: {start_time}, end: {end_time}")

        try:
            request = models.ListCallDetailRecordsRequest(
                instance_id=self.instance_id,
                start_time=start_time,
                end_time=end_time,
                page_number=page_number,
                page_size=page_size
            )

            response = self.client.list_call_detail_records(request)

            records = response.body.data.list if response.body.data else []

            logger.info(f"查询到 {len(records)} 条通话记录")
            return records

        except Exception as e:
            logger.error(f"查询通话记录失败: {str(e)}")
            raise

    async def get_call_detail(self, contact_id: str) -> dict:
        """
        获取通话详情

        Args:
            contact_id: 通话ID

        Returns:
            通话详情
        """
        if not self.client:
            raise Exception("CCC服务未初始化")

        logger.info(f"获取通话详情 - contact_id: {contact_id}")

        try:
            request = models.GetConversationDetailRequest(
                instance_id=self.instance_id,
                contact_id=contact_id
            )

            response = self.client.get_conversation_detail(request)

            detail = response.body.data

            logger.info(f"获取通话详情成功 - contact_id: {contact_id}")
            return detail

        except Exception as e:
            logger.error(f"获取通话详情失败: {str(e)}")
            raise

    async def get_recording_url(self, contact_id: str) -> str:
        """
        获取录音URL

        Args:
            contact_id: 通话ID

        Returns:
            录音文件URL
        """
        if not self.client:
            raise Exception("CCC服务未初始化")

        logger.info(f"获取录音URL - contact_id: {contact_id}")

        try:
            request = models.GetMonoRecordingRequest(
                instance_id=self.instance_id,
                contact_id=contact_id
            )

            response = self.client.get_mono_recording(request)

            # 从响应中提取录音URL
            # 响应结构: {'Code': 'OK', 'Data': {'FileUrl': '...', 'FileName': '...', 'Duration': ...}}
            if hasattr(response.body, 'data') and response.body.data:
                data = response.body.data
                if isinstance(data, dict):
                    recording_url = data.get('FileUrl', '')
                else:
                    recording_url = data.file_url if hasattr(data, 'file_url') else ''
            else:
                recording_url = ''

            if not recording_url:
                logger.warning(f"未找到录音URL - contact_id: {contact_id}")
                return None

            logger.info(f"获取录音URL成功 - contact_id: {contact_id}")
            return recording_url

        except Exception as e:
            logger.error(f"获取录音URL失败: {str(e)}")
            raise
