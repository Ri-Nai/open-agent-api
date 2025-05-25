#!/usr/bin/env python3
"""
测试运行脚本 - 统一运行所有测试
"""

import sys
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_test(test_file, description):
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"运行测试: {description}")
    print(f"文件: {test_file}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              cwd=Path(__file__).parent)
        
        print("标准输出:")
        print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - 测试通过")
        else:
            print(f"❌ {description} - 测试失败 (退出码: {result.returncode})")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ {description} - 运行异常: {e}")
        return False

def check_server_running():
    """检查服务器是否运行"""
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """主函数"""
    print("Agent API 测试套件")
    print("="*60)
    
    # 检查服务器状态
    if check_server_running():
        print("✅ 服务器正在运行")
    else:
        print("⚠️ 服务器未运行，某些测试可能失败")
        print("请先运行: python main.py")
    
    tests = [
        ("test_config.py", "配置系统测试"),
        ("simple_test.py", "简单连接测试"),
        ("test_client.py", "完整客户端测试"),
    ]
    
    print(f"\n准备运行 {len(tests)} 个测试...")
    
    results = []
    for test_file, description in tests:
        success = run_test(test_file, description)
        results.append((test_file, description, success))
    
    # 输出总结
    print(f"\n{'='*60}")
    print("测试结果总结")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for test_file, description, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{description:20} - {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed} 个通过, {failed} 个失败")
    
    if failed == 0:
        print("🎉 所有测试都通过了！")
        return 0
    else:
        print("⚠️ 有测试失败，请检查上面的错误信息")
        return 1

def interactive_mode():
    """交互模式"""
    print("Agent API 测试套件 - 交互模式")
    print("="*60)
    
    tests = {
        "1": ("test_config.py", "配置系统测试"),
        "2": ("simple_test.py", "简单连接测试"),
        "3": ("test_client.py", "完整客户端测试"),
        "4": ("debug_api.py", "API 调试工具"),
    }
    
    while True:
        print("\n选择要运行的测试:")
        for key, (file, desc) in tests.items():
            print(f"{key}. {desc}")
        print("a. 运行所有测试")
        print("0. 退出")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "0":
            break
        elif choice == "a":
            main()
        elif choice in tests:
            test_file, description = tests[choice]
            run_test(test_file, description)
        else:
            print("无效选择")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        sys.exit(main()) 
