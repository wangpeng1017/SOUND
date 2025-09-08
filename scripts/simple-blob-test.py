#!/usr/bin/env python3
"""
简化的Vercel Blob存储测试
"""

import asyncio
import httpx
import json
from datetime import datetime

# Blob存储配置
BLOB_TOKEN = "vercel_blob_rw_AUL5HsnQWN21BR8h_YbxChFzoaGO9Lb16sDGUYq3rCEVWKy"

async def test_blob_simple():
    """简化的Blob存储测试"""
    print("☁️ 测试Vercel Blob存储...")
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 测试认证和基本连接
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 尝试列出文件（测试认证）
            response = await client.get(
                "https://blob.vercel-storage.com",
                headers={"authorization": f"Bearer {BLOB_TOKEN}"}
            )
            
            print(f"\n📋 连接测试:")
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                blobs = result.get("blobs", [])
                print(f"  ✅ 连接成功")
                print(f"  📁 当前文件数量: {len(blobs)}")
                
                # 显示前几个文件
                for i, blob in enumerate(blobs[:3]):
                    print(f"    文件{i+1}: {blob.get('pathname', 'unknown')}")
                
                return True
            else:
                print(f"  ❌ 连接失败")
                print(f"  错误信息: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

async def test_token_validity():
    """测试Token有效性"""
    print("\n🔑 测试Token有效性...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 使用HEAD请求测试认证
            response = await client.head(
                "https://blob.vercel-storage.com",
                headers={"authorization": f"Bearer {BLOB_TOKEN}"}
            )
            
            if response.status_code in [200, 404]:  # 200或404都表示认证成功
                print("  ✅ Token有效")
                return True
            elif response.status_code == 401:
                print("  ❌ Token无效或已过期")
                return False
            else:
                print(f"  ⚠️ 未知状态: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"  ❌ Token测试失败: {str(e)}")
        return False

async def main():
    """主函数"""
    print("="*50)
    print("🧪 Vercel Blob存储简化测试")
    print("="*50)
    
    # 测试Token
    token_valid = await test_token_validity()
    
    # 测试连接
    connection_ok = await test_blob_simple()
    
    print(f"\n📊 测试结果:")
    print(f"  Token有效性: {'✅ 有效' if token_valid else '❌ 无效'}")
    print(f"  存储连接: {'✅ 成功' if connection_ok else '❌ 失败'}")
    
    if token_valid and connection_ok:
        print(f"\n🎉 Vercel Blob存储配置正确！")
        print(f"💡 建议: 可以在应用中使用此存储服务")
    else:
        print(f"\n⚠️ 存储配置需要检查")
        print(f"💡 建议: 检查Token是否正确或是否有权限")
    
    print(f"\n🔧 配置信息:")
    print(f"  API端点: https://blob.vercel-storage.com")
    print(f"  Token前缀: {BLOB_TOKEN[:20]}...")
    
    return token_valid and connection_ok

if __name__ == "__main__":
    asyncio.run(main())
