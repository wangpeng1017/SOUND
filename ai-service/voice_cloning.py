"""
声音克隆模块
提供声音克隆训练和推理功能
"""

import os
import json
import uuid
import asyncio
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import tempfile

from audio_processor import AudioProcessor
from tts_engine import TTSEngine

class VoiceCloningService:
    """声音克隆服务"""
    
    def __init__(self, models_dir: str = "models", cache_dir: str = "cache"):
        self.models_dir = Path(models_dir)
        self.cache_dir = Path(cache_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.audio_processor = AudioProcessor()
        self.tts_engine = TTSEngine()
        
        # 训练任务状态
        self.training_tasks = {}
        
        # 加载已有模型
        self.voice_models = self._load_existing_models()
    
    def _load_existing_models(self) -> Dict[str, Dict]:
        """加载已有的声音模型"""
        models = {}
        
        # 扫描模型目录
        for model_file in self.models_dir.glob("*.json"):
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    model_data = json.load(f)
                    voice_id = model_data.get('voice_id')
                    if voice_id:
                        models[voice_id] = model_data
            except Exception as e:
                print(f"加载模型文件失败 {model_file}: {str(e)}")
        
        return models
    
    async def start_voice_training(self, audio_file_path: str, voice_name: str, 
                                 voice_id: Optional[str] = None) -> Dict[str, any]:
        """
        开始声音训练
        
        Args:
            audio_file_path: 音频文件路径
            voice_name: 音色名称
            voice_id: 音色ID，如果为None则自动生成
            
        Returns:
            训练任务信息
        """
        if voice_id is None:
            voice_id = str(uuid.uuid4())
        
        # 验证音频文件
        validation_result = self.audio_processor.validate_audio_file(audio_file_path)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result["error"]
            }
        
        # 创建训练任务
        task_id = str(uuid.uuid4())
        task_info = {
            "task_id": task_id,
            "voice_id": voice_id,
            "voice_name": voice_name,
            "audio_file_path": audio_file_path,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "audio_info": validation_result["info"]
        }
        
        self.training_tasks[task_id] = task_info
        
        # 启动异步训练任务
        asyncio.create_task(self._train_voice_model(task_id))
        
        return {
            "success": True,
            "task_id": task_id,
            "voice_id": voice_id,
            "estimated_time": self._estimate_training_time(validation_result["info"])
        }
    
    async def _train_voice_model(self, task_id: str):
        """训练声音模型的异步任务"""
        task = self.training_tasks.get(task_id)
        if not task:
            return
        
        try:
            task["status"] = "processing"
            task["progress"] = 10
            
            # 步骤1: 音频预处理
            await self._update_task_progress(task_id, 20, "预处理音频文件...")
            processed_audio_path = await self._preprocess_audio(task["audio_file_path"])
            
            if not processed_audio_path:
                raise Exception("音频预处理失败")
            
            # 步骤2: 特征提取
            await self._update_task_progress(task_id, 40, "提取音频特征...")
            features = self.audio_processor.extract_features(processed_audio_path)
            
            if not features:
                raise Exception("特征提取失败")
            
            # 步骤3: 模型训练 (模拟)
            await self._update_task_progress(task_id, 60, "训练声音模型...")
            model_data = await self._simulate_model_training(task, features)
            
            # 步骤4: 模型验证
            await self._update_task_progress(task_id, 80, "验证模型质量...")
            validation_result = await self._validate_model(model_data)
            
            if not validation_result["valid"]:
                raise Exception(f"模型验证失败: {validation_result['error']}")
            
            # 步骤5: 保存模型
            await self._update_task_progress(task_id, 90, "保存模型...")
            model_path = self._save_voice_model(task["voice_id"], model_data)
            
            # 完成训练
            await self._update_task_progress(task_id, 100, "训练完成")
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            task["model_path"] = model_path
            
            # 添加到可用模型列表
            self.voice_models[task["voice_id"]] = model_data
            
            # 清理临时文件
            self.audio_processor.cleanup_temp_file(processed_audio_path)
            
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            task["failed_at"] = datetime.now().isoformat()
            print(f"声音训练失败 {task_id}: {str(e)}")
    
    async def _preprocess_audio(self, input_path: str) -> Optional[str]:
        """预处理音频文件"""
        try:
            output_path = self.audio_processor.create_temp_file('.wav')
            
            # 异步执行音频预处理
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None, 
                self.audio_processor.preprocess_audio,
                input_path, 
                output_path
            )
            
            if success:
                return output_path
            else:
                self.audio_processor.cleanup_temp_file(output_path)
                return None
                
        except Exception as e:
            print(f"音频预处理异常: {str(e)}")
            return None
    
    async def _simulate_model_training(self, task: Dict, features: Dict) -> Dict:
        """模拟模型训练过程"""
        # 模拟训练时间
        training_steps = 50
        for step in range(training_steps):
            progress = 60 + (step / training_steps) * 20  # 60-80%
            await self._update_task_progress(
                task["task_id"], 
                int(progress), 
                f"训练步骤 {step+1}/{training_steps}"
            )
            await asyncio.sleep(0.1)  # 模拟训练时间
        
        # 创建模型数据
        model_data = {
            "voice_id": task["voice_id"],
            "voice_name": task["voice_name"],
            "created_at": datetime.now().isoformat(),
            "audio_info": task["audio_info"],
            "features": features,
            "model_type": "simulated",
            "quality_score": features.get("quality_score", 0.8),
            "training_steps": training_steps,
            "version": "1.0"
        }
        
        return model_data
    
    async def _validate_model(self, model_data: Dict) -> Dict[str, any]:
        """验证模型质量"""
        try:
            quality_score = model_data.get("quality_score", 0)
            
            if quality_score < 0.5:
                return {
                    "valid": False,
                    "error": "音频质量不足，建议重新录制更清晰的音频"
                }
            
            return {"valid": True}
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"模型验证异常: {str(e)}"
            }
    
    def _save_voice_model(self, voice_id: str, model_data: Dict) -> str:
        """保存声音模型"""
        model_file = self.models_dir / f"{voice_id}.json"
        
        with open(model_file, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
        
        return str(model_file)
    
    async def _update_task_progress(self, task_id: str, progress: int, message: str = ""):
        """更新任务进度"""
        if task_id in self.training_tasks:
            self.training_tasks[task_id]["progress"] = progress
            self.training_tasks[task_id]["current_step"] = message
    
    def _estimate_training_time(self, audio_info: Dict) -> int:
        """估算训练时间（秒）"""
        # 根据音频时长估算训练时间
        duration = audio_info.get("duration", 10)
        base_time = 30  # 基础训练时间30秒
        duration_factor = min(duration / 10, 2)  # 时长因子，最多2倍
        
        return int(base_time * duration_factor)
    
    async def synthesize_with_voice(self, text: str, voice_id: str) -> Optional[str]:
        """使用指定音色合成语音"""
        try:
            # 检查音色是否存在
            if voice_id not in self.voice_models:
                # 如果是系统预设音色，使用TTS引擎
                return await self.tts_engine.synthesize(text, voice_id)
            
            # 使用克隆的音色 (目前使用TTS引擎模拟)
            # 在真实实现中，这里应该调用MockingBird进行推理
            model_data = self.voice_models[voice_id]
            
            # 模拟使用克隆音色的合成过程
            output_path = self.tts_engine._create_temp_audio_file()
            
            # 目前使用系统TTS作为占位符
            result = await self.tts_engine.synthesize(text, "default", output_path)
            
            return result
            
        except Exception as e:
            print(f"语音合成失败: {str(e)}")
            return None
    
    def get_training_status(self, task_id: str) -> Optional[Dict]:
        """获取训练任务状态"""
        return self.training_tasks.get(task_id)
    
    def get_available_voices(self) -> List[Dict]:
        """获取可用音色列表"""
        voices = []
        
        # 系统预设音色
        system_voices = self.tts_engine.get_available_voices()
        for voice_id, voice_name in system_voices.items():
            voices.append({
                "id": voice_id,
                "name": voice_name,
                "type": "system",
                "status": "ready"
            })
        
        # 用户克隆的音色
        for voice_id, model_data in self.voice_models.items():
            voices.append({
                "id": voice_id,
                "name": model_data["voice_name"],
                "type": "cloned",
                "status": "ready",
                "quality_score": model_data.get("quality_score", 0),
                "created_at": model_data.get("created_at")
            })
        
        return voices
    
    def delete_voice_model(self, voice_id: str) -> bool:
        """删除声音模型"""
        try:
            if voice_id in self.voice_models:
                # 删除模型文件
                model_file = self.models_dir / f"{voice_id}.json"
                if model_file.exists():
                    model_file.unlink()
                
                # 从内存中删除
                del self.voice_models[voice_id]
                
                return True
            
            return False
            
        except Exception as e:
            print(f"删除声音模型失败: {str(e)}")
            return False
