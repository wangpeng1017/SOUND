"""
TTS引擎模块
提供文字转语音功能，支持多种TTS引擎
"""

import os
import tempfile
import subprocess
import platform
from pathlib import Path
from typing import Optional, Dict, List
import asyncio
import uuid

class TTSEngine:
    """TTS引擎基类"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.available_engines = self._detect_available_engines()
        
    def _detect_available_engines(self) -> List[str]:
        """检测可用的TTS引擎"""
        engines = []
        
        # 检测系统TTS
        if self.system == "windows":
            engines.append("sapi")
        elif self.system == "darwin":  # macOS
            engines.append("say")
        elif self.system == "linux":
            # 检测espeak
            if self._command_exists("espeak"):
                engines.append("espeak")
            # 检测festival
            if self._command_exists("festival"):
                engines.append("festival")
        
        # 检测edge-tts (如果安装了)
        if self._command_exists("edge-tts"):
            engines.append("edge-tts")
            
        return engines
    
    def _command_exists(self, command: str) -> bool:
        """检查命令是否存在"""
        try:
            subprocess.run([command, "--help"], 
                         capture_output=True, 
                         timeout=5)
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    async def synthesize(self, text: str, voice_id: str = "default", 
                        output_path: Optional[str] = None) -> Optional[str]:
        """
        合成语音
        
        Args:
            text: 要合成的文本
            voice_id: 音色ID
            output_path: 输出文件路径，如果为None则自动生成
            
        Returns:
            生成的音频文件路径，失败返回None
        """
        if not text.strip():
            return None
            
        if output_path is None:
            output_path = self._create_temp_audio_file()
        
        # 根据可用引擎选择合成方法
        if "edge-tts" in self.available_engines:
            return await self._synthesize_with_edge_tts(text, voice_id, output_path)
        elif "sapi" in self.available_engines:
            return await self._synthesize_with_sapi(text, voice_id, output_path)
        elif "say" in self.available_engines:
            return await self._synthesize_with_say(text, voice_id, output_path)
        elif "espeak" in self.available_engines:
            return await self._synthesize_with_espeak(text, voice_id, output_path)
        else:
            # 如果没有可用引擎，生成静音文件
            return await self._generate_silence(text, output_path)
    
    async def _synthesize_with_edge_tts(self, text: str, voice_id: str, output_path: str) -> Optional[str]:
        """使用Edge TTS合成语音"""
        try:
            # Edge TTS中文语音
            voice_map = {
                "default": "zh-CN-XiaoxiaoNeural",
                "teacher": "zh-CN-XiaoyiNeural", 
                "mom": "zh-CN-XiaohanNeural",
                "dad": "zh-CN-YunxiNeural"
            }
            
            voice = voice_map.get(voice_id, voice_map["default"])
            
            cmd = [
                "edge-tts",
                "--voice", voice,
                "--text", text,
                "--write-media", output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                print(f"Edge TTS合成失败: {stderr.decode()}")
                return None
                
        except asyncio.TimeoutError:
            print("Edge TTS合成超时")
            return None
        except Exception as e:
            print(f"Edge TTS合成异常: {str(e)}")
            return None
    
    async def _synthesize_with_sapi(self, text: str, voice_id: str, output_path: str) -> Optional[str]:
        """使用Windows SAPI合成语音"""
        try:
            # 使用PowerShell调用SAPI
            ps_script = f'''
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.SetOutputToWaveFile("{output_path}")
            $synth.Speak("{text}")
            $synth.Dispose()
            '''
            
            process = await asyncio.create_subprocess_exec(
                "powershell", "-Command", ps_script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                return None
                
        except Exception as e:
            print(f"SAPI合成异常: {str(e)}")
            return None
    
    async def _synthesize_with_say(self, text: str, voice_id: str, output_path: str) -> Optional[str]:
        """使用macOS say命令合成语音"""
        try:
            # 先生成AIFF文件，然后转换为WAV
            temp_aiff = output_path.replace('.wav', '.aiff')
            
            cmd = ["say", "-o", temp_aiff, text]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode == 0 and os.path.exists(temp_aiff):
                # 转换为WAV格式
                convert_cmd = ["ffmpeg", "-i", temp_aiff, "-y", output_path]
                convert_process = await asyncio.create_subprocess_exec(
                    *convert_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await convert_process.communicate()
                
                # 清理临时文件
                if os.path.exists(temp_aiff):
                    os.unlink(temp_aiff)
                
                if os.path.exists(output_path):
                    return output_path
            
            return None
            
        except Exception as e:
            print(f"Say合成异常: {str(e)}")
            return None
    
    async def _synthesize_with_espeak(self, text: str, voice_id: str, output_path: str) -> Optional[str]:
        """使用espeak合成语音"""
        try:
            cmd = [
                "espeak", 
                "-v", "zh",  # 中文语音
                "-s", "150", # 语速
                "-w", output_path,  # 输出文件
                text
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                return None
                
        except Exception as e:
            print(f"Espeak合成异常: {str(e)}")
            return None
    
    async def _generate_silence(self, text: str, output_path: str) -> Optional[str]:
        """生成静音文件作为占位符"""
        try:
            # 根据文本长度生成对应时长的静音
            duration = max(1, len(text) * 0.1)  # 每个字符0.1秒
            
            # 使用ffmpeg生成静音
            cmd = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", f"anullsrc=channel_layout=mono:sample_rate=22050",
                "-t", str(duration),
                "-y", output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await asyncio.wait_for(process.communicate(), timeout=10)
            
            if process.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                # 如果ffmpeg也不可用，创建一个简单的WAV文件
                return self._create_simple_wav(duration, output_path)
                
        except Exception as e:
            print(f"生成静音文件异常: {str(e)}")
            return self._create_simple_wav(1.0, output_path)
    
    def _create_simple_wav(self, duration: float, output_path: str) -> Optional[str]:
        """创建简单的WAV文件"""
        try:
            import wave
            import struct
            
            sample_rate = 22050
            frames = int(duration * sample_rate)
            
            with wave.open(output_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # 单声道
                wav_file.setsampwidth(2)  # 16位
                wav_file.setframerate(sample_rate)
                
                # 写入静音数据
                for _ in range(frames):
                    wav_file.writeframes(struct.pack('<h', 0))
            
            return output_path
            
        except Exception as e:
            print(f"创建WAV文件失败: {str(e)}")
            return None
    
    def _create_temp_audio_file(self) -> str:
        """创建临时音频文件"""
        temp_dir = Path(tempfile.gettempdir())
        filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
        return str(temp_dir / filename)
    
    def get_available_voices(self) -> Dict[str, str]:
        """获取可用的音色列表"""
        voices = {
            "default": "默认音色",
            "teacher": "老师",
            "mom": "妈妈"
        }
        
        if "edge-tts" in self.available_engines:
            voices.update({
                "dad": "爸爸",
                "xiaoxiao": "晓晓",
                "xiaoyi": "晓伊"
            })
        
        return voices
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """清理临时文件"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception:
                pass
