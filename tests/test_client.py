#!/usr/bin/env python3
"""
Agent API 测试客户端
演示如何使用 OpenAI 风格的 Agent API
"""

import requests
import json
import sys
import time

# API 配置
API_BASE_URL = "http://localhost:8000"
API_KEY = ""  # 如果服务器启用了认证，请设置此值

def test_models():
    """测试获取模型列表"""
    print("=== 测试获取模型列表 ===")
    
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    response = requests.get(f"{API_BASE_URL}/v1/models", headers=headers)
    
    if response.status_code == 200:
        models = response.json()
        print(f"可用模型: {json.dumps(models, indent=2, ensure_ascii=False)}")
        return True
    else:
        print(f"获取模型失败: {response.status_code} - {response.text}")
        return False

def test_chat_blocking():
    """测试阻塞式聊天"""
    print("\n=== 测试阻塞式聊天 ===")
    
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    payload = {
        "model": "agent-model",
        "messages": [
            {"role": "user", "content": "你好，请介绍一下你自己"}
        ],
        "stream": False
    }
    
    print(f"发送请求: {payload['messages'][-1]['content']}")
    
    response = requests.post(f"{API_BASE_URL}/v1/chat/completions", 
                           headers=headers, 
                           json=payload)
    
    if response.status_code == 200:
        result = response.json()
        assistant_message = result["choices"][0]["message"]["content"]
        print(f"助手回复: {assistant_message}")
        return True
    else:
        print(f"聊天请求失败: {response.status_code} - {response.text}")
        return False

def test_chat_streaming():
    """测试流式聊天"""
    print("\n=== 测试流式聊天 ===")
    
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    payload = {
        "model": "agent-model",
        "messages": [
            {"role": "system", "content": "你是一个有用的助手，请用中文回答问题。"},
            {"role": "user", "content": "请写一首关于春天的短诗"}
        ],
        "stream": True
    }
    
    print(f"发送流式请求: {payload['messages'][-1]['content']}")
    print("助手回复: ", end="", flush=True)
    
    try:
        response = requests.post(f"{API_BASE_URL}/v1/chat/completions", 
                               headers=headers, 
                               json=payload, 
                               stream=True)
        
        if response.status_code == 200:
            full_response = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    line = line.strip()
                    if line.startswith("data: "):
                        data_content = line[6:]
                        if data_content == "[DONE]":
                            break
                        try:
                            data = json.loads(data_content)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    print(content, end="", flush=True)
                                    full_response += content
                        except json.JSONDecodeError:
                            continue
            
            print()  # 换行
            print(f"完整回复长度: {len(full_response)} 字符")
            return True
        else:
            print(f"流式聊天请求失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"流式聊天出错: {e}")
        return False

def test_conversation_history():
    """测试对话历史"""
    print("\n=== 测试对话历史 ===")
    
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    # 第一轮对话
    payload1 = {
        "model": "agent-model",
        "messages": [
            {"role": "user", "content": "我的名字是张三"}
        ],
        "stream": False
    }
    
    print("第一轮对话:")
    print(f"用户: {payload1['messages'][-1]['content']}")
    
    response1 = requests.post(f"{API_BASE_URL}/v1/chat/completions", 
                            headers=headers, 
                            json=payload1)
    
    if response1.status_code != 200:
        print(f"第一轮对话失败: {response1.status_code} - {response1.text}")
        return False
    
    result1 = response1.json()
    assistant_reply1 = result1["choices"][0]["message"]["content"]
    print(f"助手: {assistant_reply1}")
    
    # 第二轮对话（包含历史）
    payload2 = {
        "model": "agent-model",
        "messages": [
            {"role": "user", "content": "我的名字是张三"},
            {"role": "assistant", "content": assistant_reply1},
            {"role": "user", "content": "你还记得我的名字吗？"}
        ],
        "stream": False
    }
    
    print("\n第二轮对话:")
    print(f"用户: {payload2['messages'][-1]['content']}")
    
    response2 = requests.post(f"{API_BASE_URL}/v1/chat/completions", 
                            headers=headers, 
                            json=payload2)
    
    if response2.status_code == 200:
        result2 = response2.json()
        assistant_reply2 = result2["choices"][0]["message"]["content"]
        print(f"助手: {assistant_reply2}")
        return True
    else:
        print(f"第二轮对话失败: {response2.status_code} - {response2.text}")
        return False

def test_server_stats():
    """测试服务器统计信息"""
    print("\n=== 测试服务器统计信息 ===")
    
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    response = requests.get(f"{API_BASE_URL}/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print(f"服务器统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        return True
    else:
        print(f"获取统计信息失败: {response.status_code} - {response.text}")
        return False

def main():
    """主测试函数"""
    print("Agent API 测试客户端")
    print("=" * 50)
    
    # 测试服务器连接
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ 服务器连接正常")
        else:
            print("✗ 服务器连接异常")
            return
    except Exception as e:
        print(f"✗ 无法连接到服务器: {e}")
        print(f"请确保服务器正在运行在 {API_BASE_URL}")
        return
    
    # 运行测试
    tests = [
        ("获取模型列表", test_models),
        ("阻塞式聊天", test_chat_blocking),
        ("流式聊天", test_chat_streaming),
        ("对话历史", test_conversation_history),
        ("服务器统计", test_server_stats)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "✓" if result else "✗"))
        except Exception as e:
            print(f"测试 {test_name} 出错: {e}")
            results.append((test_name, "✗"))
    
    # 显示测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    for test_name, status in results:
        print(f"{status} {test_name}")

if __name__ == "__main__":
    main() 
