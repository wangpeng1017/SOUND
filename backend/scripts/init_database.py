#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import asyncio
import os
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import connect_database, disconnect_database
from prisma import Prisma

async def init_database():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    
    try:
        # 连接数据库
        db = await connect_database()
        print("✅ 数据库连接成功")
        
        # 检查数据库连接
        result = await db.query_raw("SELECT 1 as test")
        print(f"✅ 数据库查询测试: {result}")
        
        # 创建默认配置
        await create_default_configs(db)
        
        # 创建测试用户（开发环境）
        if os.getenv("API_DEBUG", "False").lower() == "true":
            await create_test_data(db)
        
        print("🎉 数据库初始化完成！")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {str(e)}")
        raise
    finally:
        await disconnect_database()

async def create_default_configs(db: Prisma):
    """创建默认配置"""
    print("📝 创建默认配置...")
    
    default_configs = [
        {
            "key": "app_name",
            "value": "老师喊我去上学"
        },
        {
            "key": "app_version",
            "value": "3.0.0"
        },
        {
            "key": "max_voice_duration",
            "value": "15"
        },
        {
            "key": "max_file_size",
            "value": "10485760"  # 10MB
        },
        {
            "key": "supported_audio_formats",
            "value": "mp3,wav,m4a,aac"
        }
    ]
    
    for config in default_configs:
        try:
            existing = await db.config.find_unique(where={"key": config["key"]})
            if not existing:
                await db.config.create(data=config)
                print(f"  ✅ 创建配置: {config['key']} = {config['value']}")
            else:
                print(f"  ⏭️ 配置已存在: {config['key']}")
        except Exception as e:
            print(f"  ❌ 创建配置失败 {config['key']}: {str(e)}")

async def create_test_data(db: Prisma):
    """创建测试数据（仅开发环境）"""
    print("🧪 创建测试数据...")
    
    try:
        # 创建测试用户
        test_user = await db.user.find_unique(where={"email": "test@example.com"})
        if not test_user:
            test_user = await db.user.create(
                data={
                    "email": "test@example.com",
                    "username": "testuser",
                    "nickname": "测试用户"
                }
            )
            print(f"  ✅ 创建测试用户: {test_user.id}")
        else:
            print(f"  ⏭️ 测试用户已存在: {test_user.id}")
        
        # 创建测试音色
        test_voice = await db.voice.find_first(where={"userId": test_user.id})
        if not test_voice:
            test_voice = await db.voice.create(
                data={
                    "name": "测试音色",
                    "description": "这是一个测试音色",
                    "audioUrl": "https://example.com/test-audio.mp3",
                    "audioSize": 1024000,
                    "audioDuration": 10.5,
                    "audioFormat": "audio/mp3",
                    "userId": test_user.id,
                    "status": "COMPLETED",
                    "quality": 0.85
                }
            )
            print(f"  ✅ 创建测试音色: {test_voice.id}")
        else:
            print(f"  ⏭️ 测试音色已存在: {test_voice.id}")
            
    except Exception as e:
        print(f"  ❌ 创建测试数据失败: {str(e)}")

async def check_database_status():
    """检查数据库状态"""
    print("🔍 检查数据库状态...")
    
    try:
        db = await connect_database()
        
        # 检查表是否存在
        tables = await db.query_raw("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print("📋 数据库表列表:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # 检查数据统计
        user_count = await db.user.count()
        voice_count = await db.voice.count()
        task_count = await db.task.count()
        config_count = await db.config.count()
        
        print("📊 数据统计:")
        print(f"  - 用户数量: {user_count}")
        print(f"  - 音色数量: {voice_count}")
        print(f"  - 任务数量: {task_count}")
        print(f"  - 配置数量: {config_count}")
        
    except Exception as e:
        print(f"❌ 检查数据库状态失败: {str(e)}")
        raise
    finally:
        await disconnect_database()

async def reset_database():
    """重置数据库（危险操作）"""
    print("⚠️ 重置数据库...")
    
    confirm = input("确定要重置数据库吗？这将删除所有数据！(yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ 操作已取消")
        return
    
    try:
        db = await connect_database()
        
        # 删除所有数据（保持表结构）
        await db.task.delete_many()
        await db.voice.delete_many()
        await db.user.delete_many()
        await db.config.delete_many()
        
        print("✅ 数据库已重置")
        
        # 重新创建默认数据
        await create_default_configs(db)
        
    except Exception as e:
        print(f"❌ 重置数据库失败: {str(e)}")
        raise
    finally:
        await disconnect_database()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库管理工具")
    parser.add_argument("action", choices=["init", "status", "reset"], 
                       help="操作类型: init(初始化), status(状态检查), reset(重置)")
    
    args = parser.parse_args()
    
    if args.action == "init":
        asyncio.run(init_database())
    elif args.action == "status":
        asyncio.run(check_database_status())
    elif args.action == "reset":
        asyncio.run(reset_database())

if __name__ == "__main__":
    main()
