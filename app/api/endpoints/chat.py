import time
import uuid
from typing import List
from fastapi import APIRouter, HTTPException, Response
from sse_starlette.sse import ServerSentEvent, EventSourceResponse

from app.models.chat import (
    ModelList, ModelCard, ChatCompletionRequest, ChatCompletionResponse,
    ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice,
    ChatMessage, DeltaMessage
)
from app.services.agent_service import agent_service
from app.core.auth import get_auth_dependency

router = APIRouter()

# 获取认证依赖
dependencies = get_auth_dependency()


def format_messages_for_agent(messages: List[ChatMessage]) -> str:
    """
    将 OpenAI 格式的消息列表格式化为适合后端 API 的字符串格式
    正确标注系统提示词、用户消息和助手回复
    """
    formatted_parts = []
    
    for message in messages:
        role = message.role
        content = message.content
        
        if role == "system":
            formatted_parts.append(f"[SYSTEM]: {content}")
        elif role == "user":
            formatted_parts.append(f"[USER]: {content}")
        elif role == "assistant":
            formatted_parts.append(f"[ASSISTANT]: {content}")
    
    return "\n\n".join(formatted_parts)


@router.get("/models", response_model=ModelList, dependencies=dependencies)
async def list_models():
    """获取可用模型列表"""
    return ModelList(data=[
        ModelCard(id="agent-model", owned_by="agent-api")
    ])


@router.post("/chat/completions", response_model=ChatCompletionResponse, dependencies=dependencies)
async def create_chat_completion(request: ChatCompletionRequest, response: Response):
    """创建聊天完成"""
    try:
        # 生成会话ID
        session_id = str(uuid.uuid4())
        
        # 验证消息列表不为空
        if not request.messages:
            raise HTTPException(status_code=400, detail="消息列表不能为空")
        
        # 格式化完整的对话上下文，包括系统提示词、用户消息和助手回复
        formatted_conversation = format_messages_for_agent(request.messages)
        
        if request.stream:
            # 流式响应
            def generate():
                try:
                    stream_generator = agent_service.chat_stream(session_id, formatted_conversation)
                    if not stream_generator:
                        yield ServerSentEvent(
                            data='{"error": "无法创建流式连接"}',
                            event="error"
                        )
                        return
                    
                    # 发送开始事件
                    chunk = ChatCompletionResponse(
                        model=request.model,
                        object="chat.completion.chunk",
                        choices=[ChatCompletionResponseStreamChoice(
                            index=0,
                            delta=DeltaMessage(role="assistant"),
                            finish_reason=None
                        )]
                    )
                    yield ServerSentEvent(data=chunk.json())
                    
                    # 发送内容
                    for content in stream_generator:
                        chunk = ChatCompletionResponse(
                            model=request.model,
                            object="chat.completion.chunk",
                            choices=[ChatCompletionResponseStreamChoice(
                                index=0,
                                delta=DeltaMessage(content=content),
                                finish_reason=None
                            )]
                        )
                        yield ServerSentEvent(data=chunk.json())
                    
                    # 发送结束事件
                    chunk = ChatCompletionResponse(
                        model=request.model,
                        object="chat.completion.chunk",
                        choices=[ChatCompletionResponseStreamChoice(
                            index=0,
                            delta=DeltaMessage(),
                            finish_reason="stop"
                        )]
                    )
                    yield ServerSentEvent(data=chunk.json())
                    yield ServerSentEvent(data="[DONE]")
                    
                except Exception as e:
                    yield ServerSentEvent(
                        data=f'{{"error": "流式处理错误: {str(e)}"}}',
                        event="error"
                    )
            
            return EventSourceResponse(generate())
        else:
            # 非流式响应
            answer = agent_service.chat_blocking(session_id, formatted_conversation)
            if answer is None:
                raise HTTPException(status_code=500, detail="Agent API 调用失败")
            
            return ChatCompletionResponse(
                model=request.model,
                object="chat.completion",
                choices=[ChatCompletionResponseChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=answer),
                    finish_reason="stop"
                )]
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}") 
