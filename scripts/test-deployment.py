#!/usr/bin/env python3
"""
部署测试脚本
测试前端和后端的部署状态
"""

import asyncio
import httpx
import json
from datetime import datetime

# 测试URL配置
FRONTEND_URL = "https://teacher-call-me-to-school.vercel.app"
BACKEND_URL = "https://teacher-call-backend.vercel.app"

async def test_frontend():
    """测试前端部署"""
    print("🌐 测试前端部署...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试主页
            response = await client.get(FRONTEND_URL)
            print(f"  ✅ 主页状态: {response.status_code}")
            
            # 测试PWA manifest
            response = await client.get(f"{FRONTEND_URL}/manifest.json")
            print(f"  ✅ PWA Manifest: {response.status_code}")
            
            # 测试Service Worker
            response = await client.get(f"{FRONTEND_URL}/sw.js")
            print(f"  ✅ Service Worker: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"  ❌ 前端测试失败: {str(e)}")
        return False

async def test_backend():
    """测试后端部署"""
    print("🔧 测试后端部署...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试健康检查
            response = await client.get(f"{BACKEND_URL}/health")
            print(f"  ✅ 健康检查: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  📊 服务状态: {data.get('status')}")
                print(f"  🕐 时间戳: {data.get('timestamp')}")
                print(f"  📦 版本: {data.get('version')}")
            
            # 测试API文档
            response = await client.get(f"{BACKEND_URL}/docs")
            print(f"  ✅ API文档: {response.status_code}")
            
            # 测试音色列表接口
            response = await client.get(f"{BACKEND_URL}/api/voices")
            print(f"  ✅ 音色列表API: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"  ❌ 后端测试失败: {str(e)}")
        return False

async def test_api_integration():
    """测试API集成"""
    print("🔗 测试API集成...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试用户创建
            user_data = {
                "email": f"test_{datetime.now().timestamp()}@example.com",
                "nickname": "测试用户"
            }
            
            response = await client.post(
                f"{BACKEND_URL}/api/users",
                json=user_data
            )
            print(f"  ✅ 用户创建: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    user_id = result.get("data", {}).get("user_id")
                    print(f"  👤 用户ID: {user_id}")
                    return user_id
            
            return None
            
    except Exception as e:
        print(f"  ❌ API集成测试失败: {str(e)}")
        return None

async def test_cors():
    """测试CORS配置"""
    print("🌍 测试CORS配置...")
    
    try:
        async with httpx.AsyncClient() as client:
            # 模拟前端请求
            headers = {
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
            
            response = await client.options(
                f"{BACKEND_URL}/api/voices",
                headers=headers
            )
            
            print(f"  ✅ CORS预检: {response.status_code}")
            
            # 检查CORS头
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }
            
            print(f"  🔧 CORS配置: {cors_headers}")
            
            return True
            
    except Exception as e:
        print(f"  ❌ CORS测试失败: {str(e)}")
        return False

async def test_mobile_compatibility():
    """测试移动端兼容性"""
    print("📱 测试移动端兼容性...")
    
    mobile_user_agents = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.120 Mobile Safari/537.36 MicroMessenger/8.0.10.1580"
    ]
    
    try:
        for i, ua in enumerate(mobile_user_agents):
            device_name = ["iPhone Safari", "Android Chrome", "WeChat Browser"][i]
            
            async with httpx.AsyncClient() as client:
                headers = {"User-Agent": ua}
                response = await client.get(FRONTEND_URL, headers=headers)
                print(f"  ✅ {device_name}: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 移动端兼容性测试失败: {str(e)}")
        return False

async def generate_test_report():
    """生成测试报告"""
    print("\n" + "="*50)
    print("📊 部署测试报告")
    print("="*50)
    
    results = {}
    
    # 执行所有测试
    results["frontend"] = await test_frontend()
    results["backend"] = await test_backend()
    results["api_integration"] = await test_api_integration() is not None
    results["cors"] = await test_cors()
    results["mobile"] = await test_mobile_compatibility()
    
    # 生成报告
    print("\n📋 测试结果汇总:")
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    # 总体评估
    passed_tests = sum(results.values())
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n🎯 总体评估:")
    print(f"  通过测试: {passed_tests}/{total_tests}")
    print(f"  成功率: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("  🎉 部署状态: 良好")
    elif success_rate >= 60:
        print("  ⚠️ 部署状态: 需要关注")
    else:
        print("  ❌ 部署状态: 需要修复")
    
    # 生成建议
    print(f"\n💡 建议:")
    if not results["frontend"]:
        print("  - 检查前端Vercel部署配置")
    if not results["backend"]:
        print("  - 检查后端API服务状态")
    if not results["cors"]:
        print("  - 检查CORS配置")
    if not results["mobile"]:
        print("  - 检查移动端兼容性")
    
    print(f"\n🔗 访问链接:")
    print(f"  前端应用: {FRONTEND_URL}")
    print(f"  后端API: {BACKEND_URL}")
    print(f"  API文档: {BACKEND_URL}/docs")
    
    return success_rate >= 80

async def main():
    """主函数"""
    print("🚀 开始部署测试...")
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = await generate_test_report()
    
    if success:
        print("\n🎉 部署测试完成，应用可以正常使用！")
    else:
        print("\n⚠️ 部署测试发现问题，请检查相关配置。")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
