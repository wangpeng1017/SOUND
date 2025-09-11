# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project at a glance
- Monorepo with three services:
  - frontend: Vue 3 + Vite PWA (Pinia, Vue Router). Local dev on port 3000.
  - backend: FastAPI API gateway that proxies to the AI service, manages task state, and serves audio files. Local dev on port 8000.
  - ai-service: FastAPI service implementing voice cloning and TTS endpoints. Local dev on port 8001.
- Primary dev workflow: run ai-service, then backend, then frontend. A health check script is provided.
- Production (Vercel): the repo-level vercel.json builds and serves the frontend and rewrites /api/* to a deployed backend. The backend also includes a Vercel serverless entry (backend/main_v3.py) that integrates Prisma (Python) and Vercel Blob.

Quickstart (local)
- Prereqs: Node.js 18+, Python 3.8+ (recommended 3.11), Git. Optional: FFmpeg for audio tooling.
- Start services (three terminals):
  ```bash path=null start=null
  # Terminal 1: AI service (port 8001)
  pip install -r ai-service/requirements.txt
  python ai-service/main_v2.py
  ```
  ```bash path=null start=null
  # Terminal 2: Backend API (port 8000)
  pip install -r backend/requirements.txt
  python backend/main.py
  # or: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
  ```
  ```bash path=null start=null
  # Terminal 3: Frontend (port 3000)
  cd frontend
  npm install
  npm run dev
  ```
- Verify services are up:
  ```bash path=null start=null
  python scripts/check_services.py
  ```
- Open:
  - Frontend: http://localhost:3000
  - Backend docs: http://localhost:8000/docs
  - AI service docs: http://localhost:8001/docs

Common commands
- Frontend (frontend/)
  - Dev: 
    ```bash path=null start=null
    npm run dev
    ```
  - Build/preview:
    ```bash path=null start=null
    npm run build
    npm run preview
    ```
  - Lint/format/type-check:
    ```bash path=null start=null
    npm run lint
    npm run format
    npm run type-check
    ```
- Backend (backend/)
  - Install and run:
    ```bash path=null start=null
    pip install -r backend/requirements.txt
    python backend/main.py
    # alternative Vercel-oriented app entry:
    python backend/main_v3.py
    # or: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
    ```
  - Lint (matches CI):
    ```bash path=null start=null
    pip install flake8
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    ```
  - Tests (pytest is used in CI for Python projects):
    ```bash path=null start=null
    pip install pytest pytest-asyncio
    pytest -q
    # run a single test (example):
    pytest tests/test_example.py::test_something -q
    ```
- AI service (ai-service/)
  - Install and run (v2 integrates real audio/TTS flow):
    ```bash path=null start=null
    pip install -r ai-service/requirements.txt
    python ai-service/main_v2.py
    ```
  - Lightweight mock version (simpler demo flow):
    ```bash path=null start=null
    python ai-service/main.py
    ```
  - Lint/tests (available in requirements):
    ```bash path=null start=null
    pip install flake8 black isort pytest
    flake8 .
    black .
    isort .
    pytest -q
    ```

Configuration and environment
- Frontend env files:
  - frontend/.env.development and frontend/.env.production (e.g., VITE_API_BASE_URL). In dev, Vite also proxies /api to the backend based on VITE_API_BASE_URL in vite.config.js.
- Backend environment:
  - For backend/main.py (local proxy gateway): no required envs by default; it targets AI_SERVICE_URL=http://localhost:8001 internally.
  - For backend/main_v3.py (Vercel/serverless oriented): references Prisma (Python) and Vercel Blob. You'll need at minimum:
    - PRISMA_DATABASE_URL (datasource in backend/prisma/schema.prisma)
    - BLOB_READ_WRITE_TOKEN (used by backend/app/storage.py)
- Ports (local default):
  - Frontend 3000, Backend 8000, AI service 8001.

Build and deploy (Vercel)
- Root vercel.json (repo-level) builds the frontend and rewrites API traffic:
  - Build: cd frontend && npm run build
  - Output: frontend/dist
  - Rewrites: 
    - /api/(.*) → a deployed backend endpoint
    - /(.*) → /index.html
- Frontend/vercel.json contains the same rewrites (useful if deploying the frontend directory directly).
- Backend/vercel.json configures a Python serverless function with main_v3.py.
- See VERCEL_DEPLOY.md for an end-to-end deployment walkthrough and details.

High-level architecture and key flows
- Overview
  - The backend acts as an API gateway and orchestrator. For “v2” local dev, it proxies to the ai-service (main_v2.py) for voice cloning and TTS, tracks task progress in-memory, and serves generated audio files from backend/audio.
  - The ai-service exposes endpoints for voice upload/training and TTS synthesis. Its v2 implementation runs asynchronous tasks, writes outputs to ai-service/audio_output, and reports progress via status endpoints.
  - A Vercel/serverless-oriented backend (main_v3.py) integrates persistent storage via Prisma (Python) and Vercel Blob for uploaded audio/models and maps tasks/voices to DB records. This is a more production-oriented path.
- Core endpoints and orchestration (local v2 path)
  - Get voices
    - frontend → GET /api/voices (backend/main.py)
    - backend fetches AI voices from ai-service GET /voices and returns ready voices, with local cache fallback.
  - TTS request
    - frontend → POST /api/tts { text, voice_id }
    - backend forwards to ai-service POST /synthesize, stores ai_task_id ↔ local_task_id mapping, and starts polling ai-service /synthesize/status/{ai_task_id} until completion.
    - On completion, backend exposes the audio via /api/audio/{filename}.
  - Voice sample upload
    - frontend uploads multipart form-data to backend POST /api/voice/upload
    - backend streams to ai-service /voice/upload, then polls /voice/training/status/{task_id} until status becomes ready/failed and updates voices cache.
- Notable directories and files
  - frontend/src/services/api.js: centralizes API base URL handling and API calls used by the UI.
  - backend/main.py: local gateway (v2) orchestrating AI calls and task polling.
  - backend/main_v3.py + backend/app/* + backend/prisma/schema.prisma: Vercel/serverless-oriented variant with Prisma models and Blob storage integration.
  - ai-service/main_v2.py, audio_processor.py, tts_engine.py, voice_cloning.py: AI service endpoints and processing pipeline.

CI overview (.github/workflows/ci.yml)
- Frontend: Node 18, npm ci, eslint lint, vite build, optional npm test.
- Backend: Python matrix (3.8–3.11), install requirements, flake8 lint, pytest (if tests are present).
- AI service: Python 3.9, install requirements, flake8 lint, import checks for core modules.
- Security scan: repository FS scan via Trivy with SARIF upload.

Useful utilities
- scripts/check_services.py to validate frontend/backend/ai-service availability.

Notes for future changes
- If you add or modify AI service endpoints, ensure corresponding backend routes in backend/main.py (local v2) and/or backend/main_v3.py (serverless) are updated to keep orchestration consistent.
- When switching between local v2 (in-memory) and the serverless (database/blob) path, verify env vars and DB connectivity; see backend/prisma/schema.prisma and backend/app/storage.py.

