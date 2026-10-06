# RagAI — Rag Innovations AI Chatbot

A modern, full-stack RAG (Retrieval-Augmented Generation) application for **Rag Innovations** migrated from Streamlit to a **React.js (Vite + Tailwind CSS)** frontend and **FastAPI + LangChain + Groq LLM + Mistral Embeddings** backend.

---

## 📁 Project Structure

```
RagInno(RAG)/
├── backend/                        # FastAPI Backend Application
│   ├── config.py                   # Centralized application settings & env loader
│   ├── database.py / create_database.py # Database creation & embedding persistence script
│   ├── main.py                     # FastAPI app with CORS, health check, and chat endpoints
│   ├── rag.py                      # Core RAG Service (Mistral Embeddings, ChromaDB, Groq LLM)
│   ├── schemas.py                  # Pydantic models (ChatRequest, ChatResponse, HealthResponse)
│   ├── requirements.txt            # Python backend dependencies (FastAPI, Uvicorn, LangChain, etc.)
│   └── .env.example                # Backend environment variables template
│
├── frontend/                       # React.js Frontend Application (Vite)
│   ├── public/
│   │   └── logo.png                # Official Rag Innovations Logo
│   ├── src/
│   │   ├── assets/                 # Brand assets
│   │   ├── components/
│   │   │   ├── Header.jsx          # Header with live AI health indicator & official links
│   │   │   ├── WelcomeHero.jsx     # Welcome banner with suggested quick prompt cards
│   │   │   ├── ChatMessage.jsx     # User & Assistant messages with markdown & citations
│   │   │   ├── ChatInput.jsx       # Auto-resizing input with keyboard shortcuts
│   │   │   ├── SourceModal.jsx     # Modal displaying retrieved source context & URLs
│   │   │   └── TypingIndicator.jsx # Animated typing dots with brand colors
│   │   ├── services/
│   │   │   └── api.js              # API service client for /api/chat and /api/health
│   │   ├── App.jsx                 # Main chat container with state and localStorage persistence
│   │   ├── index.css               # Brand design tokens (Crimson, CTA Orange, Warm Beige)
│   │   └── main.jsx                # React root entry point
│   ├── package.json                # Frontend dependencies (React 19, Lucide, Tailwind v4)
│   ├── vite.config.js              # Vite config with Tailwind & local backend proxy
│   ├── vercel.json                 # Vercel deployment configuration
│   └── .env.example                # Frontend environment template
│
├── RagInno_DB/                     # Persisted Chroma Vector Database
├── .env                            # Local backend API keys (GROQ_API_KEY, MISTRAL_API_KEY)
└── requirements.txt                # Root requirements
```

---

## 🚀 How to Run Locally

### 1. Backend (FastAPI)

```bash
# In the project root directory
# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies (if not already installed)
pip install -r backend/requirements.txt

# Run the backend server on port 8000
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **API Documentation (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### 2. Frontend (React.js)

```bash
# Navigate to the frontend directory
cd frontend

# Install packages
npm install

# Start Vite dev server on port 5173
npm run dev
```

- **Frontend App**: [http://localhost:5173](http://localhost:5173)

---

## 🌐 Deployment Guide

### Deploying Frontend to Vercel

1. Push your repository to GitHub.
2. In the [Vercel Dashboard](https://vercel.com), click **Add New Project** and import your repository.
3. Set **Root Directory** to `frontend`.
4. Add the Environment Variable:
   - `VITE_API_BASE_URL`: `https://your-backend-api-url.onrender.com` (your deployed backend URL).
5. Click **Deploy**.

### Deploying Backend to Render / Railway / VPS

1. Create a Web Service on [Render](https://render.com) or [Railway](https://railway.app).
2. Set **Root Directory** to `.` or `backend`.
3. Set **Build Command**: `pip install -r backend/requirements.txt`
4. Set **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Configure Environment Variables in the platform dashboard:
   - `GROQ_API_KEY`: `your_groq_api_key`
   - `MISTRAL_API_KEY`: `your_mistral_api_key`
   - `LLM_MODEL`: `openai/gpt-oss-20b`
   - `CORS_ORIGINS`: `https://your-frontend.vercel.app,http://localhost:5173`
   - `CHROMA_PERSIST_DIR`: `RagInno_DB`

---

## 🎨 Brand Design Tokens

- **Primary Crimson**: `#9c1c2b`
- **CTA Orange**: `#e4572e`
- **Warm Beige**: `#f5ecd8` / `#e6cfa3`
- **Typography**: Poppins (Google Fonts)
- **Logos & Avatars**: Official Rag Innovations branding
