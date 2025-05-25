#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API调试工具 - 专门用于测试和调试API接口
"""

import requests
import json
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.core.config import settings
    API_BASE_URL = settings.API_BASE_URL
    API_KEY = settings.API_KEY
    print(f"使用配置: {API_BASE_URL}")
except Exception as e:
    print(f"无法加载配置，使用默认值: {e}")
    API_BASE_URL = "https://agent.bit.edu.cn"
    API_KEY = "your_api_key"

def debug_request(endpoint, payload, description=""):
    """调试API请求"""
    print(f"\n{'='*60}")
    print(f"调试: {description}")
    print(f"{'='*60}")
    print(f"接口: {endpoint}")
    print(f"请求参数: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "Apikey": API_KEY,
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"\n状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"响应内容: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                return response_data
            except json.JSONDecodeError:
                print(f"响应内容 (非JSON): {response.text}")
                return None
        else:
            print(f"错误响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"请求异常: {e}")
        return None

def test_get_conversation_messages():
    """测试获取会话消息接口"""
    print("开始测试 get_conversation_messages 接口...")
    
    # 首先获取对话列表
    conversations_response = debug_request(
        "/api/proxy/api/v1/get_conversation_list",
        {"UserID": "test_user"},
        "获取对话列表"
    )
    
    if not conversations_response or not conversations_response.get("ConversationList"):
        print("没有可用的对话，先创建一个...")
        
        # 创建对话
        create_response = debug_request(
            "/api/proxy/api/v1/create_conversation",
            {"UserID": "test_user", "Inputs": {}},
            "创建测试对话"
        )
        
        if create_response and create_response.get("Conversation"):
            conv_id = create_response["Conversation"]["AppConversationID"]
        else:
            print("无法创建对话，测试终止")
            return
    else:
        conv_id = conversations_response["ConversationList"][0]["AppConversationID"]
    
    print(f"\n使用对话ID: {conv_id}")
    
    # 测试不同的参数组合
    test_cases = [
        {
            "payload": {"AppConversationID": conv_id, "UserID": "test_user"},
            "description": "基本参数"
        },
        {
            "payload": {"AppConversationID": conv_id, "UserID": "test_user", "PageSize": 10, "PageNumber": 1},
            "description": "添加分页参数"
        },
        {
            "payload": {"AppConversationID": conv_id, "UserID": "test_user", "ListOption": {"PageSize": 10, "PageNumber": 1}},
            "description": "使用ListOption"
        },
        {
            "payload": {"ConversationID": conv_id, "UserID": "test_user"},
            "description": "使用ConversationID字段"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['description']}")
        debug_request(
            "/api/proxy/api/v1/get_conversation_messages",
            test_case["payload"],
            f"获取消息历史 - {test_case['description']}"
        )

def test_other_endpoints():
    """测试其他可能有问题的接口"""
    user_id = "test_user"
    
    # 测试获取提问建议
    debug_request(
        "/api/proxy/api/v1/get_suggested_questions",
        {"AppConversationID": "test_conv_id", "UserID": user_id},
        "获取提问建议"
    )
    
    # 测试反馈接口
    debug_request(
        "/api/proxy/api/v1/feedback",
        {"AppConversationID": "test_conv_id", "UserID": user_id, "MessageID": "test_msg_id", "LikeType": 1},
        "提交反馈"
    )

def test_openai_api():
    """测试 OpenAI 风格的 API"""
    print("测试 OpenAI 风格的 API...")
    
    # 测试本地 API 服务
    local_api_url = "http://localhost:8000"
    
    # 测试获取模型列表
    try:
        response = requests.get(f"{local_api_url}/v1/models")
        print(f"模型列表状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"模型列表: {response.json()}")
    except Exception as e:
        print(f"获取模型列表失败: {e}")
    
    # 测试聊天完成
    try:
        payload = {
            "model": "agent-model",
            "messages": [
                {"role": "user", "content": "你好"}
            ],
            "stream": False
        }
        response = requests.post(f"{local_api_url}/v1/chat/completions", json=payload)
        print(f"聊天完成状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"聊天回复: {response.json()}")
        else:
            print(f"聊天失败: {response.text}")
    except Exception as e:
        print(f"聊天请求失败: {e}")

def main():
    print("API调试工具")
    print("="*60)
    print(f"当前配置:")
    print(f"  API Base URL: {API_BASE_URL}")
    print(f"  API Key: {'已配置' if API_KEY and API_KEY != 'your_api_key' else '未配置'}")
    
    while True:
        print("\n选择测试项目:")
        print("1. 测试 get_conversation_messages 接口")
        print("2. 测试其他 Agent 接口")
        print("3. 测试 OpenAI 风格 API")
        print("4. 自定义测试")
        print("0. 退出")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            test_get_conversation_messages()
        elif choice == "2":
            test_other_endpoints()
        elif choice == "3":
            test_openai_api()
        elif choice == "4":
            endpoint = input("请输入接口路径 (如: /api/proxy/api/v1/xxx): ").strip()
            payload_str = input("请输入JSON参数: ").strip()
            try:
                payload = json.loads(payload_str)
                debug_request(endpoint, payload, "自定义测试")
            except json.JSONDecodeError:
                print("JSON格式错误")
        else:
            print("无效选择")

if __name__ == "__main__":
    main() 
