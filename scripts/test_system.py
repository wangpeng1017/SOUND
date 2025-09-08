#!/usr/bin/env python3
"""
系统功能测试脚本
测试前后端集成和AI服务功能
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path

# 服务地址
BACKEND_URL = "http://localhost:8000"
AI_SERVICE_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:3000"

class SystemTester:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_service_health(self):
        """测试服务健康状态"""
        print("🔍 测试服务健康状态...")
        
        services = {
            "后端API": f"{BACKEND_URL}/health",
            "AI服务": f"{AI_SERVICE_URL}/health"
        }
        
        results = {}
        
        for name, url in services.items():
            try:
                async with self.session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        results[name] = "✅ 正常"
                        print(f"  {name}: ✅ 正常")
                    else:
                        results[name] = f"❌ 错误 ({response.status})"
                        print(f"  {name}: ❌ 错误 ({response.status})")
            except Exception as e:
                results[name] = f"❌ 连接失败: {str(e)}"
                print(f"  {name}: ❌ 连接失败: {str(e)}")
        
        return results
    
    async def test_voice_list(self):
        """测试音色列表获取"""
        print("\n🎵 测试音色列表...")
        
        try:
            async with self.session.get(f"{BACKEND_URL}/api/voices") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        voices = data.get("data", [])
                        print(f"  ✅ 获取到 {len(voices)} 个音色:")
                        for voice in voices:
                            print(f"    - {voice['name']} ({voice['id']}) - {voice['status']}")
                        return voices
                    else:
                        print("  ❌ API返回失败")
                        return []
                else:
                    print(f"  ❌ HTTP错误: {response.status}")
                    return []
        except Exception as e:
            print(f"  ❌ 请求失败: {str(e)}")
            return []
    
    async def test_tts_synthesis(self, text="你好，这是一个测试", voice_id="default"):
        """测试文字转语音"""
        print(f"\n🎤 测试文字转语音...")
        print(f"  文本: {text}")
        print(f"  音色: {voice_id}")
        
        try:
            # 发起TTS请求
            data = {
                "text": text,
                "voice_id": voice_id
            }
            
            async with self.session.post(f"{BACKEND_URL}/api/tts", json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        task_id = result["data"]["task_id"]
                        print(f"  ✅ TTS任务创建成功: {task_id}")
                        
                        # 轮询任务状态
                        return await self.poll_tts_status(task_id)
                    else:
                        print("  ❌ TTS请求失败")
                        return None
                else:
                    print(f"  ❌ HTTP错误: {response.status}")
                    return None
        except Exception as e:
            print(f"  ❌ 请求失败: {str(e)}")
            return None
    
    async def poll_tts_status(self, task_id, max_attempts=30):
        """轮询TTS任务状态"""
        print("  🔄 等待语音生成...")
        
        for attempt in range(max_attempts):
            try:
                async with self.session.get(f"{BACKEND_URL}/api/tts/status/{task_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            task_data = data["data"]
                            status = task_data["status"]
                            progress = task_data["progress"]
                            
                            if status == "completed":
                                audio_url = task_data.get("audio_url")
                                print(f"  ✅ 语音生成完成!")
                                print(f"  🎵 音频地址: {BACKEND_URL}{audio_url}")
                                return audio_url
                            elif status == "failed":
                                error = task_data.get("error", "未知错误")
                                print(f"  ❌ 语音生成失败: {error}")
                                return None
                            else:
                                print(f"  ⏳ 进度: {progress}% ({status})")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"  ⚠️ 状态查询失败: {str(e)}")
                await asyncio.sleep(1)
        
        print("  ❌ 语音生成超时")
        return None
    
    async def test_ai_service_direct(self):
        """直接测试AI服务"""
        print("\n🤖 直接测试AI服务...")
        
        try:
            # 测试音色列表
            async with self.session.get(f"{AI_SERVICE_URL}/voices") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        voices = data.get("data", [])
                        print(f"  ✅ AI服务音色列表: {len(voices)} 个")
                        for voice in voices[:3]:  # 只显示前3个
                            print(f"    - {voice['name']} ({voice.get('type', 'unknown')})")
                    else:
                        print("  ❌ AI服务音色列表获取失败")
                else:
                    print(f"  ❌ AI服务HTTP错误: {response.status}")
        except Exception as e:
            print(f"  ❌ AI服务连接失败: {str(e)}")
    
    async def test_frontend_accessibility(self):
        """测试前端可访问性"""
        print("\n🌐 测试前端可访问性...")
        
        try:
            async with self.session.get(FRONTEND_URL, timeout=5) as response:
                if response.status == 200:
                    print("  ✅ 前端应用可访问")
                    print(f"  🔗 地址: {FRONTEND_URL}")
                else:
                    print(f"  ❌ 前端HTTP错误: {response.status}")
        except Exception as e:
            print(f"  ❌ 前端连接失败: {str(e)}")
    
    async def run_full_test(self):
        """运行完整测试"""
        print("🚀 开始系统功能测试")
        print("=" * 50)
        
        # 测试服务健康状态
        health_results = await self.test_service_health()
        
        # 测试音色列表
        voices = await self.test_voice_list()
        
        # 测试AI服务
        await self.test_ai_service_direct()
        
        # 测试前端
        await self.test_frontend_accessibility()
        
        # 如果有可用音色，测试TTS
        if voices:
            voice_id = voices[0]["id"]
            await self.test_tts_synthesis("老师喊我去上学了！", voice_id)
        
        print("\n" + "=" * 50)
        print("🎯 测试总结:")
        
        all_healthy = True
        for service, status in health_results.items():
            print(f"  {service}: {status}")
            if "❌" in status:
                all_healthy = False
        
        if all_healthy:
            print("\n✅ 系统运行正常，可以开始使用!")
            print(f"🌐 前端地址: {FRONTEND_URL}")
            print(f"📚 API文档: {BACKEND_URL}/docs")
        else:
            print("\n⚠️ 部分服务存在问题，请检查服务状态")

async def main():
    """主函数"""
    async with SystemTester() as tester:
        await tester.run_full_test()

if __name__ == "__main__":
    asyncio.run(main())
