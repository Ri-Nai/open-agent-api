import json
import time
import requests
from typing import Dict, Optional, Generator
from app.core.config import settings


class AgentService:
    """Agent API 服务类"""
    
    def __init__(self):
        self.api_base_url = settings.API_BASE_URL
        self.api_key = settings.API_KEY
        self.app_id = settings.APP_ID
        self.conversations: Dict[str, Dict] = {}  # 存储会话ID映射
        self.conversation_timestamps: Dict[str, float] = {}  # 存储会话时间戳
        
    def cleanup_old_conversations(self):
        """清理过期的会话"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, timestamp in self.conversation_timestamps.items():
            if current_time - timestamp > settings.CONVERSATION_TIMEOUT:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            if session_id in self.conversations:
                del self.conversations[session_id]
            if session_id in self.conversation_timestamps:
                del self.conversation_timestamps[session_id]
        
        # 如果会话数量超过限制，删除最旧的会话
        if len(self.conversations) > settings.MAX_CONVERSATIONS:
            sorted_sessions = sorted(self.conversation_timestamps.items(), key=lambda x: x[1])
            sessions_to_remove = len(self.conversations) - settings.MAX_CONVERSATIONS
            
            for i in range(sessions_to_remove):
                session_id = sorted_sessions[i][0]
                if session_id in self.conversations:
                    del self.conversations[session_id]
                if session_id in self.conversation_timestamps:
                    del self.conversation_timestamps[session_id]
        
    def make_api_request(self, endpoint: str, method: str = "POST", data: Optional[Dict] = None) -> Optional[Dict]:
        """执行 API 请求并返回 JSON 响应"""
        url = f"{self.api_base_url}{endpoint}"
        headers = {
            "Apikey": self.api_key,
            "Content-Type": "application/json"
        }
        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data, timeout=30)
            else:
                return None

            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API 请求错误: {e}")
            return None

    def make_streaming_request(self, endpoint: str, data: Optional[Dict] = None):
        """执行流式 API 请求"""
        url = f"{self.api_base_url}{endpoint}"
        headers = {
            "Apikey": self.api_key,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream; charset=utf-8"
        }
        try:
            response = requests.post(url, headers=headers, json=data, stream=True, timeout=60)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response
        except Exception as e:
            print(f"流式请求错误: {e}")
            return None

    def parse_sse_line(self, line: str) -> Optional[Dict]:
        """解析SSE格式的单行数据"""
        line = line.strip()
        if line.startswith("data:"):
            data_content = line[5:].strip()
            if data_content and data_content != "[DONE]":
                try:
                    return json.loads(data_content)
                except json.JSONDecodeError:
                    return None
        return None

    def create_conversation(self, user_id: str, inputs: Optional[Dict] = None) -> Optional[str]:
        """创建新的会话"""
        endpoint = "/api/proxy/api/v1/create_conversation"
        payload = {
            "UserID": user_id,
            "Inputs": inputs or {}
        }
        
        response_data = self.make_api_request(endpoint, method="POST", data=payload)
        
        if response_data and response_data.get("Conversation") and response_data["Conversation"].get("AppConversationID"):
            return response_data["Conversation"]["AppConversationID"]
        return None

    def get_or_create_conversation(self, session_id: str) -> Optional[Dict]:
        """获取或创建会话"""
        # 清理过期会话
        self.cleanup_old_conversations()
        
        if session_id not in self.conversations:
            user_id = f"user_{session_id}"
            app_conversation_id = self.create_conversation(user_id)
            if app_conversation_id:
                self.conversations[session_id] = {
                    "app_conversation_id": app_conversation_id,
                    "user_id": user_id
                }
                self.conversation_timestamps[session_id] = time.time()
            else:
                return None
        else:
            # 更新时间戳
            self.conversation_timestamps[session_id] = time.time()
            
        return self.conversations[session_id]

    def chat_stream(self, session_id: str, conversation_content: str) -> Optional[Generator[str, None, None]]:
        """流式聊天 - 现在接受完整的格式化对话内容，包括系统提示词和对话历史"""
        conv_info = self.get_or_create_conversation(session_id)
        if not conv_info:
            return None
            
        endpoint = "/api/proxy/api/v1/chat_query_v2"
        payload = {
            "AppConversationID": conv_info["app_conversation_id"],
            "UserID": conv_info["user_id"],
            "Query": conversation_content,
            "ResponseMode": "streaming"
        }

        response = self.make_streaming_request(endpoint, data=payload)
        if not response:
            return None

        def generate():
            for line in response.iter_lines(decode_unicode=True, chunk_size=1):
                if line:
                    line = line.strip()
                    if settings.VERBOSE_LOGGING:
                        print(f"[DEBUG] 收到行: {line}")
                    data = self.parse_sse_line(line)
                    if data:
                        if settings.VERBOSE_LOGGING:
                            print(f"[DEBUG] 解析数据: {data}")
                        event = data.get("event")
                        
                        if event == "message_start":
                            # 消息开始，可以记录任务ID等信息
                            task_id = data.get("task_id")
                            continue
                        elif event == "message":
                            answer_part = data.get("answer", "")
                            if answer_part:
                                if settings.VERBOSE_LOGGING:
                                    print(f"[DEBUG] 输出内容: {answer_part}")
                                yield answer_part
                        elif event == "message_end":
                            if settings.VERBOSE_LOGGING:
                                print("[DEBUG] 消息结束")
                            break
                        elif event == "message_failed":
                            error_msg = data.get("error", "未知错误")
                            print(f"[ERROR] 消息失败: {error_msg}")
                            break

        return generate()

    def chat_blocking(self, session_id: str, conversation_content: str) -> Optional[str]:
        """阻塞式聊天 - 现在接受完整的格式化对话内容，包括系统提示词和对话历史"""
        conv_info = self.get_or_create_conversation(session_id)
        if not conv_info:
            return None
            
        endpoint = "/api/proxy/api/v1/chat_query_v2"
        payload = {
            "AppConversationID": conv_info["app_conversation_id"],
            "UserID": conv_info["user_id"],
            "Query": conversation_content,
            "ResponseMode": "blocking"
        }

        response_data = self.make_api_request(endpoint, method="POST", data=payload)
        
        if response_data and "answer" in response_data:
            return response_data["answer"]
        return None


# 创建全局服务实例
agent_service = AgentService() 
