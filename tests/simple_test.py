import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_streaming():
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "model": "agent-model",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "stream": True
    }
    
    print("发送流式请求...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/v1/chat/completions", 
                               headers=headers, 
                               json=payload, 
                               stream=True)
        
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
