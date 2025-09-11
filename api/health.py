from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="API Health")

@app.get("/")
@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
