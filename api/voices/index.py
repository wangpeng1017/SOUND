from fastapi import FastAPI

app = FastAPI(title="Voices API", version="0.1.3-minimal-nocors")

SYSTEM_VOICES = [
    {"id": "teacher-female", "name": "女老师", "status": "ready"},
    {"id": "teacher-male", "name": "男老师", "status": "ready"},
    {"id": "mom", "name": "妈妈", "status": "ready"},
    {"id": "dad", "name": "爸爸", "status": "ready"},
]

@app.get("/")
async def list_voices_root():
    return {"success": True, "data": SYSTEM_VOICES}
