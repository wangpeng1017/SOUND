from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="API Health")

@app.get("/")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
