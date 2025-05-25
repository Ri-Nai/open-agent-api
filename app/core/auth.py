from fastapi import HTTPException, Header, Depends
from app.core.config import settings


def verify_api_key(Authorization: str = Header(None)):
    """验证 API 密钥"""
    if not settings.API_AUTH_KEY:
        return True
    
    if Authorization and Authorization.startswith("Bearer "):
        token = Authorization[7:]
        if token == settings.API_AUTH_KEY:
            return True
    
    raise HTTPException(status_code=403, detail="Unauthorized")


# 依赖项
def get_auth_dependency():
    """获取认证依赖项"""
    return [Depends(verify_api_key)] if settings.API_AUTH_KEY else [] 
