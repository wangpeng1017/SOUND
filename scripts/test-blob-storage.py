#!/usr/bin/env python3
"""
Vercel Blob存储测试脚本
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
import uuid

# Blob存储配置
BLOB_TOKEN = "vercel_blob_rw_AUL5HsnQWN21BR8h_YbxChFzoaGO9Lb16sDGUYq3rCEVWKy"
BLOB_API_URL = "https://blob.vercel-storage.com"

async def test_blob_upload():
    """测试文件上传"""
    print("📤 测试文件上传...")
    
    try:
        # 创建测试文件内容
        test_content = f"Test file created at {datetime.now().isoformat()}"
        test_filename = f"upload-test-{uuid.uuid4().hex[:8]}.txt"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(
                BLOB_API_URL,
                headers={
                    "authorization": f"Bearer {BLOB_TOKEN}",
                    "x-content-type": "text/plain"
                },
                params={"filename": test_filename},
                content=test_content.encode()
            )
            
            if response.status_code == 200:
                result = response.json()
                file_url = result.get("url")
                print(f"✅ 文件上传成功")
                print(f"  文件名: {test_filename}")
                print(f"  文件URL: {file_url}")
                print(f"  文件大小: {len(test_content)} bytes")
                return file_url
            else:
                print(f"❌ 文件上传失败: {response.status_code}")
                print(f"  错误信息: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ 上传测试失败: {str(e)}")
        return None

async def test_blob_download(file_url):
    """测试文件下载"""
    print("📥 测试文件下载...")
    
    if not file_url:
        print("⏭️ 跳过下载测试（没有可用的文件URL）")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(file_url)
            
            if response.status_code == 200:
                content = response.text
                print(f"✅ 文件下载成功")
                print(f"  内容长度: {len(content)} 字符")
                print(f"  内容预览: {content[:50]}...")
                return True
            else:
                print(f"❌ 文件下载失败: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ 下载测试失败: {str(e)}")
        return False

async def test_blob_list():
    """测试文件列表"""
    print("📋 测试文件列表...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                BLOB_API_URL,
                headers={"authorization": f"Bearer {BLOB_TOKEN}"},
                params={"limit": "10"}
            )
            
            if response.status_code == 200:
                result = response.json()
                blobs = result.get("blobs", [])
                print(f"✅ 文件列表获取成功")
                print(f"  测试文件数量: {len(blobs)}")
                
                for i, blob in enumerate(blobs[:3]):  # 只显示前3个
                    print(f"  文件{i+1}: {blob.get('pathname', 'unknown')}")
                
                return True
            else:
                print(f"❌ 文件列表获取失败: {response.status_code}")
                print(f"  错误信息: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 列表测试失败: {str(e)}")
        return False

async def test_blob_delete(file_url):
    """测试文件删除"""
    print("🗑️ 测试文件删除...")
    
    if not file_url:
        print("⏭️ 跳过删除测试（没有可用的文件URL）")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                file_url,
                headers={"authorization": f"Bearer {BLOB_TOKEN}"}
            )
            
            if response.status_code == 200:
                print("✅ 文件删除成功")
                return True
            else:
                print(f"❌ 文件删除失败: {response.status_code}")
                print(f"  错误信息: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 删除测试失败: {str(e)}")
        return False

async def test_audio_upload():
    """测试音频文件上传"""
    print("🎵 测试音频文件上传...")
    
    try:
        # 创建模拟音频文件内容（实际应用中会是真实的音频数据）
        audio_content = b"RIFF" + b"\x00" * 100  # 简单的音频文件头
        audio_filename = f"test-audio-{uuid.uuid4().hex[:8]}.wav"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(
                BLOB_API_URL,
                headers={
                    "authorization": f"Bearer {BLOB_TOKEN}",
                    "x-content-type": "audio/wav"
                },
                params={"filename": audio_filename},
                content=audio_content
            )
            
            if response.status_code == 200:
                result = response.json()
                file_url = result.get("url")
                print(f"✅ 音频文件上传成功")
                print(f"  文件名: {audio_filename}")
                print(f"  文件URL: {file_url}")
                print(f"  文件大小: {len(audio_content)} bytes")
                return file_url
            else:
                print(f"❌ 音频文件上传失败: {response.status_code}")
                print(f"  错误信息: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ 音频上传测试失败: {str(e)}")
        return None

async def test_large_file_upload():
    """测试大文件上传"""
    print("📦 测试大文件上传...")
    
    try:
        # 创建1MB的测试文件
        large_content = b"A" * (1024 * 1024)  # 1MB
        large_filename = f"large-file-{uuid.uuid4().hex[:8]}.bin"
        
        async with httpx.AsyncClient(timeout=60.0) as client:  # 增加超时时间
            response = await client.put(
                BLOB_API_URL,
                headers={
                    "authorization": f"Bearer {BLOB_TOKEN}",
                    "x-content-type": "application/octet-stream"
                },
                params={"filename": large_filename},
                content=large_content
            )
            
            if response.status_code == 200:
                result = response.json()
                file_url = result.get("url")
                print(f"✅ 大文件上传成功")
                print(f"  文件大小: {len(large_content) / 1024 / 1024:.1f} MB")
                print(f"  文件URL: {file_url}")
                
                # 立即删除大文件以节省存储空间
                await test_blob_delete(file_url)
                
                return True
            else:
                print(f"❌ 大文件上传失败: {response.status_code}")
                print(f"  错误信息: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 大文件上传测试失败: {str(e)}")
        return False

async def generate_storage_report():
    """生成存储测试报告"""
    print("\n" + "="*50)
    print("☁️ Vercel Blob存储测试报告")
    print("="*50)
    
    # 执行所有测试
    upload_url = await test_blob_upload()
    download_ok = await test_blob_download(upload_url)
    list_ok = await test_blob_list()
    audio_url = await test_audio_upload()
    large_file_ok = await test_large_file_upload()
    delete_ok = await test_blob_delete(upload_url)
    
    # 清理音频测试文件
    if audio_url:
        await test_blob_delete(audio_url)
    
    print(f"\n📋 测试结果汇总:")
    print(f"  文件上传: {'✅ 成功' if upload_url else '❌ 失败'}")
    print(f"  文件下载: {'✅ 成功' if download_ok else '❌ 失败'}")
    print(f"  文件列表: {'✅ 成功' if list_ok else '❌ 失败'}")
    print(f"  音频上传: {'✅ 成功' if audio_url else '❌ 失败'}")
    print(f"  大文件上传: {'✅ 成功' if large_file_ok else '❌ 失败'}")
    print(f"  文件删除: {'✅ 成功' if delete_ok else '❌ 失败'}")
    
    print(f"\n🔧 存储配置:")
    print(f"  API端点: {BLOB_API_URL}")
    print(f"  认证令牌: {BLOB_TOKEN[:20]}...")
    print(f"  支持格式: 文本、音频、二进制")
    
    # 总体评估
    total_tests = 6
    passed_tests = sum([
        bool(upload_url), download_ok, list_ok, 
        bool(audio_url), large_file_ok, delete_ok
    ])
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n🎯 存储评估:")
    print(f"  通过测试: {passed_tests}/{total_tests}")
    print(f"  成功率: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("  🎉 存储状态: 优秀")
    elif success_rate >= 60:
        print("  ⚠️ 存储状态: 良好")
    else:
        print("  ❌ 存储状态: 需要修复")
    
    print(f"\n💡 使用建议:")
    print("  - 音频文件建议使用 voices/ 前缀")
    print("  - 模型文件建议使用 models/ 前缀")
    print("  - 临时文件建议使用 temp/ 前缀")
    print("  - 定期清理测试文件以节省存储空间")
    
    return success_rate >= 60

async def main():
    """主函数"""
    print("☁️ 开始Vercel Blob存储测试...")
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = await generate_storage_report()
    
    if success:
        print("\n🎉 Blob存储测试完成，存储服务正常！")
    else:
        print("\n⚠️ 存储测试完成，但存在一些问题，请检查配置。")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
