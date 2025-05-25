import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import chat
from app.core.config import settings

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    app = FastAPI(
        title="Agent API",
        description="OpenAI 风格的 Agent API",
        version="1.0.0"
    )
    
    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(chat.router, prefix="/v1", tags=["chat"])
    
    # 健康检查和根路由
    @app.get("/")
    async def root():
        return {"message": "Agent API 服务正在运行", "version": "1.0.0"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    @app.get("/stats")
    async def stats():
        from app.services.agent_service import agent_service
        return {
            "active_conversations": len(agent_service.conversations),
            "total_conversations": len(agent_service.conversation_timestamps)
        }
    
    return app 
