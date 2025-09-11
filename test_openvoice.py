#!/usr/bin/env python3
"""
OpenVoice TTS 功能测试脚本
测试语音克隆功能是否正常工作
"""

import asyncio
import httpx
import json
import base64

# 测试配置
BASE_URL = "https://sound.aifly.me"  # 生产环境
# BASE_URL = "http://localhost:8000"  # 本地环境

async def test_openvoice():
    """测试OpenVoice语音克隆功能"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("=" * 50)
        print("OpenVoice TTS 功能测试")
        print("=" * 50)
        
        # 1. 获取音色列表
        print("\n1. 获取音色列表...")
        voices_resp = await client.get(f"{BASE_URL}/api/voices")
        if voices_resp.status_code == 200:
            voices = voices_resp.json()
            print(f"   找到 {len(voices.get('data', []))} 个音色")
            
            # 查找克隆音色
            cloned_voices = [v for v in voices.get('data', []) if v['id'] != 'default']
            if cloned_voices:
                test_voice = cloned_voices[0]
                print(f"   使用音色: {test_voice['name']} (ID: {test_voice['id']})")
            else:
                test_voice = None
                print("   未找到克隆音色，将使用默认音色")
        else:
            print(f"   获取音色列表失败: {voices_resp.status_code}")
            test_voice = None
        
        # 2. 测试TTS
        print("\n2. 测试文字转语音...")
        test_text = "你好，这是OpenVoice语音克隆测试。今天天气真不错！"
        
        tts_data = {
            "text": test_text,
            "voice_id": test_voice['id'] if test_voice else "default"
        }
        
        print(f"   文本: {test_text}")
        print(f"   音色: {tts_data['voice_id']}")
        
        # 发起TTS请求
        tts_resp = await client.post(
            f"{BASE_URL}/api/tts",
            json=tts_data
        )
        
        if tts_resp.status_code == 200:
            result = tts_resp.json()
            if result.get('success'):
                task_id = result['data']['task_id']
                print(f"   任务创建成功: {task_id}")
                
                # 3. 轮询任务状态
                print("\n3. 等待语音生成...")
                for i in range(30):  # 最多等待30秒
                    await asyncio.sleep(1)
                    
                    status_resp = await client.get(
                        f"{BASE_URL}/api/tts/status/{task_id}"
                    )
                    
                    if status_resp.status_code == 200:
                        status_data = status_resp.json()
                        if status_data.get('success'):
                            task = status_data['data']
                            
                            if task['status'] == 'completed':
                                print(f"   ✓ 语音生成成功!")
                                print(f"   音频URL: {task.get('audio_url')}")
                                print(f"   生成方法: {task.get('method', 'unknown')}")
                                
                                # 尝试下载音频验证
                                if task.get('audio_url'):
                                    audio_url = task['audio_url']
                                    if not audio_url.startswith('http'):
                                        audio_url = f"{BASE_URL}{audio_url}"
                                    
                                    print(f"\n4. 验证音频文件...")
                                    audio_resp = await client.get(audio_url)
                                    if audio_resp.status_code == 200:
                                        audio_size = len(audio_resp.content)
                                        print(f"   ✓ 音频文件可访问 (大小: {audio_size:,} 字节)")
                                    else:
                                        print(f"   ✗ 音频文件无法访问: {audio_resp.status_code}")
                                
                                break
                            
                            elif task['status'] == 'failed':
                                print(f"   ✗ 语音生成失败: {task.get('error')}")
                                break
                            
                            else:
                                print(f"   进度: {task.get('progress', 0)}%", end='\r')
                else:
                    print("\n   ✗ 生成超时")
            else:
                print(f"   ✗ 创建任务失败: {result}")
        else:
            print(f"   ✗ TTS请求失败: {tts_resp.status_code}")
            print(f"   响应: {tts_resp.text}")
        
        print("\n" + "=" * 50)
        print("测试完成")
        print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_openvoice())
