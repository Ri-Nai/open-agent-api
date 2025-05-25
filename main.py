#!/usr/bin/env python3
"""
Agent API 主入口文件
"""
import uvicorn
from app import create_app
from app.core.config import settings

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    ) 
