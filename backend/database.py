"""
简化的数据库连接模块 - Vercel部署版本
"""

import os
import asyncio
from typing import Optional, Dict, List, Any
import json
from datetime import datetime

# 模拟数据库存储（生产环境应使用真实数据库）
_memory_db = {
    "users": {},
    "voices": {},
    "tasks": {},
    "configs": {
        "app_name": "老师喊我去上学",
        "app_version": "3.0.0",
        "max_voice_duration": "15",
        "max_file_size": "10485760"
    }
}

class MockDatabase:
    """模拟数据库类"""
    
    def __init__(self):
        self.connected = False
    
    async def connect(self):
        """连接数据库"""
        self.connected = True
        return self
    
    async def disconnect(self):
        """断开连接"""
        self.connected = False
    
    # 用户相关操作
    class user:
        @staticmethod
        async def find_unique(where: Dict):
            """查找唯一用户"""
            for user_id, user in _memory_db["users"].items():
                if where.get("id") == user_id:
                    return type('User', (), user)()
                if where.get("email") == user.get("email"):
                    return type('User', (), user)()
                if where.get("wechatOpenId") == user.get("wechatOpenId"):
                    return type('User', (), user)()
            return None
        
        @staticmethod
        async def create(data: Dict):
            """创建用户"""
            user_id = f"user_{len(_memory_db['users']) + 1}"
            user_data = {
                "id": user_id,
                "email": data.get("email"),
                "username": data.get("username"),
                "nickname": data.get("nickname"),
                "wechatOpenId": data.get("wechatOpenId"),
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            }
            _memory_db["users"][user_id] = user_data
            return type('User', (), user_data)()
    
    # 音色相关操作
    class voice:
        @staticmethod
        async def find_unique(where: Dict):
            """查找唯一音色"""
            for voice_id, voice in _memory_db["voices"].items():
                if where.get("id") == voice_id:
                    return type('Voice', (), voice)()
            return None
        
        @staticmethod
        async def find_many(where: Dict = None, skip: int = 0, take: int = 20, order_by: Dict = None):
            """查找多个音色"""
            voices = list(_memory_db["voices"].values())
            
            # 简单过滤
            if where:
                if where.get("userId"):
                    voices = [v for v in voices if v.get("userId") == where["userId"]]
                if where.get("status"):
                    voices = [v for v in voices if v.get("status") == where["status"]]
            
            # 分页
            voices = voices[skip:skip + take]
            
            return [type('Voice', (), voice)() for voice in voices]
        
        @staticmethod
        async def count(where: Dict = None):
            """统计音色数量"""
            voices = list(_memory_db["voices"].values())
            
            if where:
                if where.get("userId"):
                    voices = [v for v in voices if v.get("userId") == where["userId"]]
                if where.get("status"):
                    voices = [v for v in voices if v.get("status") == where["status"]]
            
            return len(voices)
        
        @staticmethod
        async def create(data: Dict):
            """创建音色"""
            voice_id = f"voice_{len(_memory_db['voices']) + 1}"
            voice_data = {
                "id": voice_id,
                "name": data.get("name"),
                "description": data.get("description"),
                "audioUrl": data.get("audioUrl"),
                "audioSize": data.get("audioSize"),
                "audioDuration": data.get("audioDuration"),
                "audioFormat": data.get("audioFormat"),
                "userId": data.get("userId"),
                "status": data.get("status", "PENDING"),
                "quality": data.get("quality"),
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            }
            _memory_db["voices"][voice_id] = voice_data
            return type('Voice', (), voice_data)()
        
        @staticmethod
        async def delete(where: Dict):
            """删除音色"""
            voice_id = where.get("id")
            if voice_id in _memory_db["voices"]:
                del _memory_db["voices"][voice_id]
                return True
            return False
    
    # 任务相关操作
    class task:
        @staticmethod
        async def find_unique(where: Dict):
            """查找唯一任务"""
            for task_id, task in _memory_db["tasks"].items():
                if where.get("id") == task_id:
                    return type('Task', (), task)()
            return None
        
        @staticmethod
        async def create(data: Dict):
            """创建任务"""
            task_id = f"task_{len(_memory_db['tasks']) + 1}"
            task_data = {
                "id": task_id,
                "type": data.get("type"),
                "status": data.get("status", "PENDING"),
                "inputText": data.get("inputText"),
                "voiceId": data.get("voiceId"),
                "userId": data.get("userId"),
                "progress": data.get("progress", 0),
                "error": data.get("error"),
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            }
            _memory_db["tasks"][task_id] = task_data
            return type('Task', (), task_data)()
        
        @staticmethod
        async def update(where: Dict, data: Dict):
            """更新任务"""
            task_id = where.get("id")
            if task_id in _memory_db["tasks"]:
                _memory_db["tasks"][task_id].update(data)
                _memory_db["tasks"][task_id]["updatedAt"] = datetime.now().isoformat()
                return type('Task', (), _memory_db["tasks"][task_id])()
            return None
    
    # 配置相关操作
    class config:
        @staticmethod
        async def find_unique(where: Dict):
            """查找配置"""
            key = where.get("key")
            if key in _memory_db["configs"]:
                return type('Config', (), {
                    "id": key,
                    "key": key,
                    "value": _memory_db["configs"][key]
                })()
            return None
        
        @staticmethod
        async def create(data: Dict):
            """创建配置"""
            key = data.get("key")
            value = data.get("value")
            _memory_db["configs"][key] = value
            return type('Config', (), {
                "id": key,
                "key": key,
                "value": value
            })()
        
        @staticmethod
        async def count():
            """统计配置数量"""
            return len(_memory_db["configs"])

# 全局数据库实例
db: Optional[MockDatabase] = None

async def connect_database():
    """连接数据库"""
    global db
    if db is None:
        db = MockDatabase()
        await db.connect()
    return db

async def disconnect_database():
    """断开数据库连接"""
    global db
    if db is not None:
        await db.disconnect()
        db = None

async def get_database():
    """获取数据库连接"""
    database = await connect_database()
    return database

async def init_database():
    """初始化数据库"""
    database = await connect_database()
    print("✅ 模拟数据库初始化完成")
    return database
