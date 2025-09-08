"""
AI语音服务 - 主服务文件 v2
集成真实的音频处理和TTS功能
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os
import tempfile
import uuid
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import json

# 导入自定义模块
from audio_processor import AudioProcessor
from tts_engine import TTSEngine
from voice_cloning import VoiceCloningService

# 创建FastAPI应用
app = FastAPI(
    title="AI语音服务 v2",
    description="提供声音克隆和语音合成功能 - 集成真实AI处理",
    version="2.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建必要的目录
UPLOAD_DIR = Path("uploads")
MODELS_DIR = Path("models")
AUDIO_OUTPUT_DIR = Path("audio_output")
TEMP_DIR = Path("temp")

for directory in [UPLOAD_DIR, MODELS_DIR, AUDIO_OUTPUT_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# 初始化服务组件
audio_processor = AudioProcessor()
tts_engine = TTSEngine()
voice_cloning_service = VoiceCloningService(str(MODELS_DIR), str(TEMP_DIR))

# 任务存储
synthesis_tasks = {}

@app.get("/")
async def root():
    """根路径，返回服务信息"""
    return {
        "service": "AI语音服务 v2",
        "version": "2.0.0",
        "status": "running",
        "features": ["真实TTS", "声音克隆", "音频处理"],
        "available_engines": tts_engine.available_engines
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "tts_engine": "available" if tts_engine.available_engines else "limited",
            "audio_processor": "available",
            "voice_cloning": "available"
        },
        "available_tts_engines": tts_engine.available_engines
    }

@app.get("/voices")
async def get_available_voices():
    """获取可用音色列表"""
    try:
        voices = voice_cloning_service.get_available_voices()
        
        return {
            "success": True,
            "data": voices,
            "total": len(voices)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取音色列表失败: {str(e)}")

@app.post("/synthesize")
async def synthesize_speech(
    text: str = Form(...),
    voice_id: str = Form("default"),
    speed: float = Form(1.0),
    pitch: float = Form(1.0)
):
    """语音合成"""
    try:
        # 验证输入
        if not text.strip():
            raise HTTPException(status_code=400, detail="文本不能为空")
        
        if len(text) > 500:
            raise HTTPException(status_code=400, detail="文本长度不能超过500字符")
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建合成任务
        task = {
            "id": task_id,
            "text": text,
            "voice_id": voice_id,
            "status": "processing",
            "progress": 0,
            "audio_url": None,
            "created_at": datetime.now().isoformat()
        }
        
        synthesis_tasks[task_id] = task
        
        # 启动异步合成任务
        asyncio.create_task(process_synthesis_task(task_id))
        
        return {
            "success": True,
            "data": {
                "task_id": task_id,
                "status": "processing",
                "message": "正在生成语音..."
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")

@app.get("/synthesize/status/{task_id}")
async def get_synthesis_status(task_id: str):
    """获取合成任务状态"""
    if task_id not in synthesis_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = synthesis_tasks[task_id]
    
    return {
        "success": True,
        "data": {
            "task_id": task_id,
            "status": task["status"],
            "progress": task["progress"],
            "audio_url": task["audio_url"],
            "text": task["text"],
            "voice_id": task["voice_id"],
            "error": task.get("error")
        }
    }

@app.post("/voice/upload")
async def upload_voice_sample(
    audio_file: UploadFile = File(...),
    voice_name: str = Form(...)
):
    """上传音频样本用于声音克隆"""
    try:
        # 验证文件类型
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="请上传音频文件")
        
        # 验证音色名称
        if not voice_name.strip() or len(voice_name) > 20:
            raise HTTPException(status_code=400, detail="音色名称长度应在1-20字符之间")
        
        # 保存上传文件
        upload_id = str(uuid.uuid4())
        file_extension = os.path.splitext(audio_file.filename or "audio.wav")[1]
        file_path = UPLOAD_DIR / f"{upload_id}{file_extension}"
        
        content = await audio_file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 验证音频文件
        validation_result = audio_processor.validate_audio_file(str(file_path))
        if not validation_result["valid"]:
            # 删除无效文件
            file_path.unlink()
            raise HTTPException(status_code=400, detail=validation_result["error"])
        
        # 开始声音训练
        training_result = await voice_cloning_service.start_voice_training(
            str(file_path), 
            voice_name.strip()
        )
        
        if not training_result["success"]:
            # 删除文件
            file_path.unlink()
            raise HTTPException(status_code=400, detail=training_result["error"])
        
        return {
            "success": True,
            "data": {
                "upload_id": upload_id,
                "task_id": training_result["task_id"],
                "voice_id": training_result["voice_id"],
                "voice_name": voice_name,
                "status": "training",
                "estimated_time": training_result["estimated_time"],
                "audio_info": validation_result["info"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.get("/voice/training/status/{task_id}")
async def get_training_status(task_id: str):
    """获取声音训练状态"""
    task = voice_cloning_service.get_training_status(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="训练任务不存在")
    
    return {
        "success": True,
        "data": {
            "task_id": task_id,
            "voice_id": task["voice_id"],
            "voice_name": task["voice_name"],
            "status": task["status"],
            "progress": task["progress"],
            "current_step": task.get("current_step", ""),
            "created_at": task["created_at"],
            "completed_at": task.get("completed_at"),
            "error": task.get("error")
        }
    }

@app.delete("/voice/{voice_id}")
async def delete_voice(voice_id: str):
    """删除音色"""
    try:
        success = voice_cloning_service.delete_voice_model(voice_id)
        
        if success:
            return {
                "success": True,
                "message": "音色删除成功"
            }
        else:
            raise HTTPException(status_code=404, detail="音色不存在")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """获取音频文件"""
    file_path = AUDIO_OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

# ==================== 异步任务处理 ====================

async def process_synthesis_task(task_id: str):
    """处理语音合成任务"""
    try:
        task = synthesis_tasks[task_id]
        
        # 更新进度
        task["progress"] = 20
        
        # 使用声音克隆服务进行合成
        audio_path = await voice_cloning_service.synthesize_with_voice(
            task["text"], 
            task["voice_id"]
        )
        
        task["progress"] = 80
        
        if audio_path and os.path.exists(audio_path):
            # 移动文件到输出目录
            audio_filename = f"synthesis_{task_id}.wav"
            output_path = AUDIO_OUTPUT_DIR / audio_filename
            
            import shutil
            shutil.move(audio_path, output_path)
            
            # 更新任务状态
            task["status"] = "completed"
            task["progress"] = 100
            task["audio_url"] = f"/audio/{audio_filename}"
            task["completed_at"] = datetime.now().isoformat()
        else:
            raise Exception("语音合成失败")
            
    except Exception as e:
        task["status"] = "failed"
        task["error"] = str(e)
        print(f"合成任务失败 {task_id}: {str(e)}")

if __name__ == "__main__":
    print("🎤 AI语音服务 v2 启动中...")
    print("🔧 集成真实音频处理和TTS功能")
    print("🌐 API文档: http://localhost:8001/docs")
    
    uvicorn.run(
        "main_v2:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
