"""
音频处理模块
提供音频文件的验证、预处理、格式转换等功能
"""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict
import wave
import struct
import math

class AudioProcessor:
    """音频处理器"""
    
    def __init__(self):
        self.supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
        self.target_sample_rate = 22050  # MockingBird推荐的采样率
        self.target_channels = 1  # 单声道
        
    def validate_audio_file(self, file_path: str) -> Dict[str, any]:
        """
        验证音频文件
        返回音频信息或错误信息
        """
        try:
            file_path = Path(file_path)
            
            # 检查文件是否存在
            if not file_path.exists():
                return {"valid": False, "error": "文件不存在"}
            
            # 检查文件扩展名
            if file_path.suffix.lower() not in self.supported_formats:
                return {"valid": False, "error": f"不支持的文件格式，支持格式：{', '.join(self.supported_formats)}"}
            
            # 检查文件大小 (最大10MB)
            file_size = file_path.stat().st_size
            if file_size > 10 * 1024 * 1024:
                return {"valid": False, "error": "文件过大，请上传小于10MB的音频文件"}
            
            # 获取音频信息
            audio_info = self._get_audio_info(str(file_path))
            
            if not audio_info:
                return {"valid": False, "error": "无法读取音频文件信息"}
            
            # 检查时长 (5秒到30秒)
            duration = audio_info.get('duration', 0)
            if duration < 3:
                return {"valid": False, "error": "音频时长太短，至少需要3秒"}
            if duration > 60:
                return {"valid": False, "error": "音频时长太长，最多支持60秒"}
            
            return {
                "valid": True,
                "info": {
                    "duration": duration,
                    "sample_rate": audio_info.get('sample_rate'),
                    "channels": audio_info.get('channels'),
                    "file_size": file_size,
                    "format": file_path.suffix.lower()
                }
            }
            
        except Exception as e:
            return {"valid": False, "error": f"音频文件验证失败: {str(e)}"}
    
    def _get_audio_info(self, file_path: str) -> Optional[Dict]:
        """获取音频文件信息"""
        try:
            # 使用ffprobe获取音频信息
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                # 如果ffprobe不可用，尝试简单的WAV文件解析
                return self._parse_wav_info(file_path)
            
            import json
            data = json.loads(result.stdout)
            
            # 查找音频流
            audio_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    audio_stream = stream
                    break
            
            if not audio_stream:
                return None
            
            return {
                'duration': float(audio_stream.get('duration', 0)),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0))
            }
            
        except Exception:
            # 回退到简单的WAV解析
            return self._parse_wav_info(file_path)
    
    def _parse_wav_info(self, file_path: str) -> Optional[Dict]:
        """简单的WAV文件信息解析"""
        try:
            with wave.open(file_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                duration = frames / sample_rate
                
                return {
                    'duration': duration,
                    'sample_rate': sample_rate,
                    'channels': channels
                }
        except Exception:
            return None
    
    def preprocess_audio(self, input_path: str, output_path: str) -> bool:
        """
        预处理音频文件
        转换为MockingBird需要的格式
        """
        try:
            # 使用ffmpeg进行音频预处理
            cmd = [
                'ffmpeg', '-i', input_path,
                '-ar', str(self.target_sample_rate),  # 设置采样率
                '-ac', str(self.target_channels),     # 设置声道数
                '-acodec', 'pcm_s16le',              # 设置编码格式
                '-y',                                # 覆盖输出文件
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True
            else:
                print(f"音频预处理失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("音频预处理超时")
            return False
        except Exception as e:
            print(f"音频预处理异常: {str(e)}")
            # 如果ffmpeg不可用，尝试简单的复制
            try:
                import shutil
                shutil.copy2(input_path, output_path)
                return True
            except Exception:
                return False
    
    def extract_features(self, audio_path: str) -> Optional[Dict]:
        """
        提取音频特征
        为声音克隆做准备
        """
        try:
            # 这里应该集成真实的特征提取算法
            # 目前返回模拟数据
            validation_result = self.validate_audio_file(audio_path)
            
            if not validation_result["valid"]:
                return None
            
            audio_info = validation_result["info"]
            
            # 模拟特征提取
            features = {
                "mfcc": [0.1, 0.2, 0.3] * 13,  # 模拟MFCC特征
                "pitch": {
                    "mean": 150.0,
                    "std": 20.0,
                    "min": 100.0,
                    "max": 200.0
                },
                "energy": {
                    "mean": 0.5,
                    "std": 0.1
                },
                "duration": audio_info["duration"],
                "quality_score": self._calculate_quality_score(audio_info)
            }
            
            return features
            
        except Exception as e:
            print(f"特征提取失败: {str(e)}")
            return None
    
    def _calculate_quality_score(self, audio_info: Dict) -> float:
        """计算音频质量分数 (0-1)"""
        score = 1.0
        
        # 根据采样率评分
        sample_rate = audio_info.get("sample_rate", 0)
        if sample_rate < 16000:
            score *= 0.7
        elif sample_rate < 22050:
            score *= 0.9
        
        # 根据时长评分
        duration = audio_info.get("duration", 0)
        if duration < 5:
            score *= 0.8
        elif duration > 30:
            score *= 0.9
        
        # 根据声道数评分
        channels = audio_info.get("channels", 1)
        if channels > 2:
            score *= 0.9
        
        return min(1.0, max(0.0, score))
    
    def create_temp_file(self, suffix: str = '.wav') -> str:
        """创建临时文件"""
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        temp_file.close()
        return temp_file.name
    
    def cleanup_temp_file(self, file_path: str):
        """清理临时文件"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass
