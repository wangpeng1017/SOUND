#!/usr/bin/env python3
"""
简单的服务状态检查脚本
"""

import requests
import time

def check_service(name, url):
    """检查单个服务状态"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: 正常运行")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: 连接失败")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {name}: 连接超时")
        return False
    except Exception as e:
        print(f"❌ {name}: 错误 - {str(e)}")
        return False

def main():
    print("🔍 检查服务状态...")
    print("-" * 30)
    
    services = {
        "前端应用": "http://localhost:3000",
        "后端API": "http://localhost:8000/health",
        "AI服务": "http://localhost:8001/health"
    }
    
    all_ok = True
    for name, url in services.items():
        if not check_service(name, url):
            all_ok = False
    
    print("-" * 30)
    if all_ok:
        print("🎉 所有服务运行正常!")
        print("🌐 前端地址: http://localhost:3000")
        print("📚 API文档: http://localhost:8000/docs")
    else:
        print("⚠️ 部分服务未运行，请检查启动状态")

if __name__ == "__main__":
    main()
