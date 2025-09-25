#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单交互式聊天 - Open Agent API
轻量级版本，专注于核心对话功能
"""

import requests
import json
import sys

# 配置
API_BASE_URL = "http://localhost:8000"
API_KEY = ""  # 如果需要认证，请设置API密钥

def check_server():
    """检查服务器状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_message(messages, stream=True):
    """发送消息到API"""
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    payload = {
        "model": "agent-model",
        "messages": messages,
        "stream": stream
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            stream=stream
        )
        
        if response.status_code == 200:
            if stream:
                return handle_stream_response(response)
            else:
                result = response.json()
                return result["choices"][0]["message"]["content"]
        else:
            return f"错误: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"请求失败: {e}"

def handle_stream_response(response):
    """处理流式响应"""
    print("🤖 助手: ", end="", flush=True)
    full_response = ""
    
    try:
        for line in response.iter_lines(decode_unicode=True):
            if line and line.strip().startswith("data: "):
                data_content = line.strip()[6:]
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
        return full_response
    
    except Exception as e:
        print(f"\n处理响应出错: {e}")
        return ""

def main():
    """主程序"""
    print("🚀 Open Agent API 简单聊天程序")
    print("=" * 40)
    
    # 检查服务器
    if not check_server():
        print(f"❌ 无法连接到服务器: {API_BASE_URL}")
        print("请确保服务器正在运行")
        return
    
    print("✅ 服务器连接正常")
    print("💡 输入 'quit' 或 'exit' 退出，输入 'clear' 清除历史")
    print("🎉 开始对话吧！")
    print("-" * 40)
    
    # 对话历史
    messages = []
    
    try:
        while True:
            # 获取用户输入
            user_input = input("\n👤 您: ").strip()
            
            if not user_input:
                continue
            
            # 处理退出命令
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            # 处理清除命令
            if user_input.lower() in ['clear', '清除']:
                messages = []
                print("✅ 对话历史已清除")
                continue
            
            # 添加用户消息
            messages.append({"role": "user", "content": user_input})
            
            # 发送请求并获取回复
            assistant_reply = send_message(messages, stream=True)
            
            if assistant_reply and not assistant_reply.startswith("错误") and not assistant_reply.startswith("请求失败"):
                # 添加助手回复到历史
                messages.append({"role": "assistant", "content": assistant_reply})
            else:
                # 如果出错，移除刚添加的用户消息
                messages.pop()
                print(f"❌ {assistant_reply}")
    
    except KeyboardInterrupt:
        print("\n👋 再见！")
    except EOFError:
        print("\n👋 再见！")
    except Exception as e:
        print(f"\n程序出错: {e}")

if __name__ == "__main__":
    main()