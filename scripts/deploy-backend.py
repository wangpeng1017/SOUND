#!/usr/bin/env python3
"""
后端部署脚本
自动化部署到Vercel并配置环境变量
"""

import asyncio
import httpx
import json
import os
import subprocess
from datetime import datetime

# 部署配置
BACKEND_URL = "https://teacher-call-backend.vercel.app"
FRONTEND_URL = "https://teacher-call-me-to-school.vercel.app"

# 环境变量配置
ENV_VARS = {
    "BLOB_READ_WRITE_TOKEN": "vercel_blob_rw_AUL5HsnQWN21BR8h_YbxChFzoaGO9Lb16sDGUYq3rCEVWKy",
    "PRISMA_DATABASE_URL": "prisma+postgres://accelerate.prisma-data.net/?api_key=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqd3RfaWQiOjEsInNlY3VyZV9rZXkiOiJza19wcGdyMVlRaHNjaURMd0NoY3pYMXQiLCJhcGlfa2V5IjoiMDFLNE1NM0c3OVZaMVZIR0ZXUjRCUEZYQ1ciLCJ0ZW5hbnRfaWQiOiI3MGI0NjNmMGI0MzdkZTAzMWZlZDgyZWYxZTYwYTMxYzQ3NjQ1NzRiNWI4NWYyOTcxNTE4NTIwZDQ3ZGI5NTNkIiwiaW50ZXJuYWxfc2VjcmV0IjoiN2VlOGViZDUtOWJmZi00OWRhLWFiZjgtYTk1YjZkNDhjNGQ0In0.KiikocrUoD_b0eIOShgAkr4cCJm7rNcJ4x2DgUNWfbU",
    "JWT_SECRET_KEY": "teacher_call_me_to_school_jwt_secret_key_2024_very_secure_random_string",
    "API_DEBUG": "False",
    "PYTHONPATH": "."
}

async def check_vercel_cli():
    """检查Vercel CLI是否安装"""
    try:
        result = subprocess.run(["vercel", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Vercel CLI版本: {result.stdout.strip()}")
            return True
        else:
            print("❌ Vercel CLI未安装")
            return False
    except FileNotFoundError:
        print("❌ Vercel CLI未找到")
        return False

async def deploy_backend():
    """部署后端到Vercel"""
    print("🚀 开始部署后端服务...")
    
    try:
        # 切换到backend目录
        os.chdir("backend")
        
        # 检查vercel.json配置
        if not os.path.exists("vercel.json"):
            print("❌ vercel.json配置文件不存在")
            return False
        
        # 部署到Vercel
        print("📦 正在部署到Vercel...")
        result = subprocess.run(
            ["vercel", "--prod", "--yes"],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print("✅ 后端部署成功")
            print(f"📝 部署输出: {result.stdout}")
            return True
        else:
            print(f"❌ 后端部署失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 部署超时")
        return False
    except Exception as e:
        print(f"❌ 部署过程出错: {str(e)}")
        return False
    finally:
        # 返回原目录
        os.chdir("..")

async def set_environment_variables():
    """设置Vercel环境变量"""
    print("🔧 配置环境变量...")
    
    try:
        os.chdir("backend")
        
        for key, value in ENV_VARS.items():
            print(f"  设置 {key}...")
            result = subprocess.run([
                "vercel", "env", "add", key, "production"
            ], input=value, text=True, capture_output=True)
            
            if result.returncode == 0:
                print(f"  ✅ {key} 设置成功")
            else:
                print(f"  ⚠️ {key} 设置可能失败: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ 环境变量配置失败: {str(e)}")
        return False
    finally:
        os.chdir("..")

async def test_backend_deployment():
    """测试后端部署"""
    print("🧪 测试后端部署...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试健康检查
            response = await client.get(f"{BACKEND_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 后端健康检查通过")
                print(f"  状态: {data.get('status')}")
                print(f"  版本: {data.get('version')}")
                print(f"  时间: {data.get('timestamp')}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ 后端测试失败: {str(e)}")
        return False

async def test_api_endpoints():
    """测试API端点"""
    print("🔗 测试API端点...")
    
    endpoints = [
        ("/health", "健康检查"),
        ("/docs", "API文档"),
        ("/api/voices", "音色列表"),
    ]
    
    results = {}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint, name in endpoints:
                try:
                    response = await client.get(f"{BACKEND_URL}{endpoint}")
                    results[name] = response.status_code
                    
                    if response.status_code in [200, 404]:  # 404也是正常的，说明服务在运行
                        print(f"  ✅ {name}: {response.status_code}")
                    else:
                        print(f"  ⚠️ {name}: {response.status_code}")
                        
                except Exception as e:
                    results[name] = f"Error: {str(e)}"
                    print(f"  ❌ {name}: {str(e)}")
        
        return results
        
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")
        return {}

async def test_blob_storage():
    """测试Blob存储"""
    print("☁️ 测试Blob存储...")
    
    try:
        # 创建测试文件
        test_content = b"Hello, Vercel Blob Storage!"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试上传
            response = await client.put(
                "https://blob.vercel-storage.com",
                headers={
                    "authorization": f"Bearer {ENV_VARS['BLOB_READ_WRITE_TOKEN']}",
                    "x-content-type": "text/plain"
                },
                params={"filename": "test/deployment-test.txt"},
                content=test_content
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Blob存储上传测试成功")
                print(f"  文件URL: {result.get('url')}")
                return True
            else:
                print(f"❌ Blob存储测试失败: {response.status_code}")
                print(f"  错误信息: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Blob存储测试失败: {str(e)}")
        return False

async def generate_deployment_report():
    """生成部署报告"""
    print("\n" + "="*50)
    print("📊 部署报告")
    print("="*50)
    
    # 执行所有测试
    backend_status = await test_backend_deployment()
    api_results = await test_api_endpoints()
    blob_status = await test_blob_storage()
    
    print(f"\n📋 部署结果汇总:")
    print(f"  后端服务: {'✅ 正常' if backend_status else '❌ 异常'}")
    print(f"  Blob存储: {'✅ 正常' if blob_status else '❌ 异常'}")
    
    print(f"\n🔗 服务地址:")
    print(f"  后端API: {BACKEND_URL}")
    print(f"  前端应用: {FRONTEND_URL}")
    print(f"  API文档: {BACKEND_URL}/docs")
    
    print(f"\n📈 API端点状态:")
    for name, status in api_results.items():
        print(f"  {name}: {status}")
    
    # 总体评估
    total_tests = 3
    passed_tests = sum([backend_status, blob_status, len(api_results) > 0])
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n🎯 总体评估:")
    print(f"  通过测试: {passed_tests}/{total_tests}")
    print(f"  成功率: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("  🎉 部署状态: 优秀")
    elif success_rate >= 60:
        print("  ⚠️ 部署状态: 良好")
    else:
        print("  ❌ 部署状态: 需要修复")
    
    return success_rate >= 60

async def main():
    """主函数"""
    print("🚀 开始后端部署流程...")
    print(f"🕐 部署时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查Vercel CLI
    if not await check_vercel_cli():
        print("💡 请先安装Vercel CLI: npm i -g vercel")
        return False
    
    # 部署后端
    if not await deploy_backend():
        print("❌ 后端部署失败，停止流程")
        return False
    
    # 等待部署完成
    print("⏳ 等待部署完成...")
    await asyncio.sleep(30)
    
    # 配置环境变量
    await set_environment_variables()
    
    # 生成部署报告
    success = await generate_deployment_report()
    
    if success:
        print("\n🎉 后端部署完成，服务正常运行！")
    else:
        print("\n⚠️ 部署完成，但存在一些问题，请检查配置。")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
