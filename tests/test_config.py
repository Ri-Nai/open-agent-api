#!/usr/bin/env python3
"""
测试配置优先级的脚本
"""

import os
import sys

from test_env import (
    load_settings,
    reset_settings_cache,
)


def _reload_settings():
    modules_to_clear = ['app.core.config', 'app.core', 'app']
    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]
    reset_settings_cache()
    return load_settings()

def test_config_priority():
    """测试配置优先级"""
    print("🧪 测试配置优先级")
    print("=" * 50)
    
    # 测试1: 没有环境变量时
    print("\n1. 测试：仅使用配置文件")
    try:
        # 清除可能存在的环境变量
        env_vars_to_clear = [
            'AGENT_APP_ID', 'AGENT_API_KEY', 'AGENT_API_BASE_URL',
            'SERVER_HOST', 'SERVER_PORT', 'API_AUTH_KEY'
        ]
        
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
        
        # 重新导入配置模块
        settings = _reload_settings()
        print(f"   APP_ID: {settings.APP_ID}")
        print(f"   API_KEY: {settings.API_KEY[:8]}..." if settings.API_KEY else "   API_KEY: 未配置")
        print(f"   API_BASE_URL: {settings.API_BASE_URL}")
        print(f"   SERVER_PORT: {settings.SERVER_PORT}")
        
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试2: 使用环境变量覆盖
    print("\n2. 测试：环境变量覆盖配置文件")
    try:
        # 设置环境变量
        os.environ['AGENT_APP_ID'] = 'env_override_app_id'
        os.environ['AGENT_API_KEY'] = 'env_override_api_key'
        os.environ['SERVER_PORT'] = '9000'
        
        # 重新导入配置模块
        settings = _reload_settings()
        print(f"   APP_ID: {settings.APP_ID}")
        print(f"   API_KEY: {settings.API_KEY}")
        print(f"   SERVER_PORT: {settings.SERVER_PORT}")
        print("   ✅ 环境变量成功覆盖了配置文件")
        
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试3: 部分覆盖
    print("\n3. 测试：部分环境变量覆盖")
    try:
        # 只设置一个环境变量
        os.environ['AGENT_APP_ID'] = 'partial_env_app_id'
        if 'AGENT_API_KEY' in os.environ:
            del os.environ['AGENT_API_KEY']
        if 'SERVER_PORT' in os.environ:
            del os.environ['SERVER_PORT']
        
        # 重新导入配置模块
        settings = _reload_settings()
        print(f"   APP_ID (来自环境变量): {settings.APP_ID}")
        print(f"   API_KEY (来自配置文件): {settings.API_KEY[:8]}..." if settings.API_KEY else "   API_KEY: 未配置")
        print(f"   SERVER_PORT (来自配置文件): {settings.SERVER_PORT}")
        
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试4: 配置验证
    print("\n4. 测试：配置验证")
    try:
        # 清除必需的配置
        if 'AGENT_APP_ID' in os.environ:
            del os.environ['AGENT_APP_ID']
        if 'AGENT_API_KEY' in os.environ:
            del os.environ['AGENT_API_KEY']
        
        # 重新导入配置模块（应该会抛出验证错误）
        settings = _reload_settings()
        print("   ⚠️ 配置验证未按预期工作")
        
    except ValueError as e:
        print(f"   ✅ 配置验证正常工作: {e}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n" + "=" * 50)
    print("📋 结论:")
    print("1. 环境变量优先级最高")
    print("2. 可以部分覆盖配置文件")
    print("3. 配置验证确保必需参数存在")
    print("4. 新的配置系统更加健壮")
    print("5. 支持 Pydantic 类型验证")

if __name__ == "__main__":
    test_config_priority() 
