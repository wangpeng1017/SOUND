from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Voices API", version="0.1.2-minimal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 极简内存音色（始终可用）
SYSTEM_VOICES = [
    {"id": "teacher-female", "name": "女老师", "status": "ready"},
    {"id": "teacher-male", "name": "男老师", "status": "ready"},
    {"id": "mom", "name": "妈妈", "status": "ready"},
    {"id": "dad", "name": "爸爸", "status": "ready"},
]

@app.get("/")
@app.get("/api/voices")
async def list_voices():
    # 返回固定的系统音色，验证函数运行无误
    return {"success": True, "data": SYSTEM_VOICES}
