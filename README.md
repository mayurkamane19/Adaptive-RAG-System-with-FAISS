# Adaptive RAG SaaS Dashboard

FastAPI + React SaaS dashboard with:

- Adaptive RAG backend endpoints
- Auth flow with protected routes
- SQLite-backed persistence
- CRUD for users, billing, reports, and notifications
- Backend-driven charts and overview cards

## Project Structure

```text
adaptive-rag-system/
|
|-- app/
|   |-- main.py
|   |-- api/routes.py
|   |-- core/config.py
|   |-- services/saas_store.py
|
|-- frontend/
|   |-- App.jsx
|   |-- api/client.js
|   |-- pages/
|   |-- components/
|   |-- package.json
|   |-- vite.config.js
|
|-- data/
|   |-- saas_app.db
|   |-- documents/
|
|-- requirements.txt
|-- .env.example
```

## Local Setup

### 1. Backend

```powershell
cd "C:\Users\mayur\OneDrive\Documents\New project\adaptive-rag-system"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a local env file from `.env.example` if needed.

Run backend:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Useful URLs:

- API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 2. Frontend

```powershell
cd "C:\Users\mayur\OneDrive\Documents\New project\adaptive-rag-system\frontend"
npm install
```

Create `.env` from `frontend/.env.example`:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Run frontend:

```powershell
npm run dev
```

Frontend URL:

- [http://localhost:5173](http://localhost:5173)

## Demo Login

```text
Email: demo@pulsestack.com
Password: 123456
```

## Production Build

### Frontend build

```powershell
cd frontend
npm install
npm run build
```

Preview production build locally:

```powershell
npm run preview:host
```

Built output:

```text
frontend/dist
```

### Backend production run

Use the same project root:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Environment Variables

### Backend

```text
API_HOST=127.0.0.1
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
LLM_PROVIDER=offline
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b
ENABLE_SEMANTIC_EMBEDDINGS=false
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Frontend

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Hosting Notes

### Option 1: Split hosting

- Deploy FastAPI backend on a Python host like Render, Railway, Azure App Service, or a VPS
- Deploy `frontend/dist` on Vercel, Netlify, or static hosting
- Set frontend `VITE_API_BASE_URL` to the deployed backend URL
- Set backend `CORS_ORIGINS` to the deployed frontend URL

Example:

```text
VITE_API_BASE_URL=https://your-backend.example.com
CORS_ORIGINS=https://your-frontend.example.com
```

### Option 2: Same server hosting

- Build frontend with `npm run build`
- Serve `frontend/dist`
- Run FastAPI on the same machine
- Reverse proxy both through Nginx or Caddy

Suggested routing:

```text
/ -> frontend static files
/api -> FastAPI backend
/docs -> FastAPI docs
```

## Current CRUD Coverage

- Users: add/delete
- Billing: add/delete
- Reports: add/delete
- Notifications: add/delete

## Quick Verification

After deployment, verify:

1. `GET /health` returns `{"status":"ok"}`
2. Frontend loads login page
3. Demo login works
4. Users and Billing CRUD persists after refresh
5. Reports and Notifications actions persist after refresh

## Test

```powershell
pytest
```
