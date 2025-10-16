import json

import requests

from test_env import build_headers, get_local_server_base_url

API_BASE_URL = get_local_server_base_url()

def test_streaming():
    headers = build_headers("application/json")
    
    payload = {
        "model": "agent-model",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "stream": True
    }
    
    print("发送流式请求...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            stream=True,
            timeout=30,
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        
        if response.status_code == 200:
            print("开始接收流式数据:")
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    print(f"收到行: {line}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求出错: {e}")

if __name__ == "__main__":
    test_streaming() 
