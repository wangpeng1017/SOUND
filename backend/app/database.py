"""
数据库连接和配置
"""

import os
from typing import Optional
from prisma import Prisma
from contextlib import asynccontextmanager

# 全局数据库实例
db: Optional[Prisma] = None

async def connect_database():
    """连接数据库"""
    global db
    if db is None:
        db = Prisma()
        await db.connect()
    return db

async def disconnect_database():
    """断开数据库连接"""
    global db
    if db is not None:
        await db.disconnect()
        db = None

@asynccontextmanager
async def get_database():
    """获取数据库连接的上下文管理器"""
    database = await connect_database()
    try:
        yield database
    finally:
        # 保持连接，不在这里断开
        pass

async def init_database():
    """初始化数据库"""
    database = await connect_database()
    
    # 这里可以添加初始化数据
    # 例如创建默认配置等
    
    return database
