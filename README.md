# RAG Chatbot - Production Deployment

A production-ready Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents, processes them into vector embeddings stored in Supabase PostgreSQL, and enables a chat interface to ask questions about document content using OpenAI's GPT models.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Vercel    │─────▶│   Railway    │─────▶│  Supabase   │
│  (Frontend) │      │  (Backend)   │      │  (pgvector) │
│   React     │      │  FastAPI     │      │  PostgreSQL │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    OpenAI    │
                     │ (Embeddings) │
                     └──────────────┘
```

### Components

- **Frontend**: React (Vite) deployed on Vercel
- **Backend**: FastAPI (Python) containerized and deployed on Railway
- **Vector Database**: Supabase PostgreSQL with pgvector extension
- **Embeddings**: OpenAI text-embedding-3-small
- **LLM**: OpenAI GPT-3.5-turbo

## Prerequisites

Before deploying, ensure you have:

1. **Supabase Account** (free tier available)
2. **Railway Account** (free tier available)
3. **Vercel Account** (free tier available)
4. **OpenAI API Key** (with credits for GPT-3.5-turbo and embeddings)
5. **GitHub Account** (for connecting repositories)

## Deployment Steps

### Step 1: Set Up Supabase Database

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** in your Supabase dashboard
3. Open `backend/supabase_setup.sql` from this repository
4. Copy and paste the entire SQL script into the SQL Editor
5. Click **Run** to execute the script
6. Verify the `documents` table was created:
   - Go to **Table Editor**
   - You should see the `documents` table with columns: `id`, `content`, `embedding`, `metadata`, `source`, `created_at`

### Step 2: Get Database Connection String

1. In Supabase dashboard, go to **Settings** → **Database**
2. Find **Connection string** section
3. Copy the **URI** connection string (starts with `postgresql://`)
4. Save this for Step 4

### Step 3: Prepare GitHub Repository

1. Push this codebase to a GitHub repository
2. Ensure all files are committed and pushed

### Step 4: Deploy Backend to Railway

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repository
4. Railway will detect the `railway.toml` and `Dockerfile`
5. Once the build starts, go to **Variables** tab
6. Add the following environment variables:

   ```
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   OPENAI_API_KEY=sk-your-key-here
   FRONTEND_URL=https://your-frontend.vercel.app
   EMBEDDING_MODEL=text-embedding-3-small
   LLM_MODEL=gpt-3.5-turbo
   EMBEDDING_DIMENSION=1536
   RETRIEVAL_K=3
   LOG_LEVEL=INFO
   ```

   **Important**: 
   - Replace `DATABASE_URL` with the connection string from Step 2
   - Replace `FRONTEND_URL` with your Vercel URL (you'll get this in Step 5)
   - Use your actual OpenAI API key

7. Railway will automatically deploy. Wait for deployment to complete.
8. Copy your Railway service URL (e.g., `https://your-app.railway.app`)

### Step 5: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **Add New Project**
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend` (if your frontend is in a subdirectory)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add environment variable:
   - **Name**: `VITE_API_URL`
   - **Value**: Your Railway backend URL from Step 4 (e.g., `https://your-app.railway.app`)
6. Click **Deploy**
7. Once deployed, copy your Vercel URL (e.g., `https://your-app.vercel.app`)

### Step 6: Update CORS Configuration

1. Go back to Railway dashboard
2. Update the `FRONTEND_URL` environment variable with your actual Vercel URL
3. Railway will automatically redeploy

### Step 7: Test the Application

1. Open your Vercel frontend URL
2. Upload a PDF document
3. Wait for processing (check Railway logs if issues occur)
4. Ask a question about the document
5. Verify the response

## Local Development

### Backend Setup

See [backend/README.md](./backend/README.md) for local development instructions.

### Frontend Setup

1. Navigate to `frontend` directory
2. Install dependencies: `npm install`
3. Create `.env` file with:
   ```
   VITE_API_URL=http://localhost:8000
   ```
4. Run development server: `npm run dev`

## Common Issues & Troubleshooting

### Database Connection Failures

**Symptoms**: Backend logs show "connection refused" or "database does not exist"

**Solutions**:
- Verify `DATABASE_URL` is correctly formatted: `postgresql://user:password@host:port/database`
- Check Supabase project is active (not paused)
- Ensure IP allowlist in Supabase allows Railway IPs (or set to allow all)
- Verify pgvector extension is enabled: Run `SELECT * FROM pg_extension WHERE extname = 'vector';` in Supabase SQL Editor

### CORS Errors

**Symptoms**: Browser console shows CORS policy errors

**Solutions**:
- Verify `FRONTEND_URL` in Railway matches your Vercel URL exactly (including `https://`)
- Check for trailing slashes (should not have one)
- Clear browser cache and hard refresh
- Verify backend `/health` endpoint is accessible

### Embedding Dimension Mismatch

**Symptoms**: Errors about vector dimension mismatch

**Solutions**:
- Ensure `EMBEDDING_DIMENSION` matches your embedding model:
  - `text-embedding-3-small`: 1536
  - `text-embedding-3-large`: 3072
- Update Supabase table if needed: `ALTER TABLE documents ALTER COLUMN embedding TYPE vector(3072);` (for large model)
- Re-run the SQL setup script if you change dimensions

### Free-Tier Rate Limits

**Symptoms**: API calls fail with rate limit errors

**Solutions**:
- OpenAI: Check your usage limits in OpenAI dashboard
- Supabase: Free tier has connection limits; consider connection pooling (already configured)
- Railway: Free tier has usage limits; monitor in dashboard
- Vercel: Free tier has bandwidth limits

### Document Upload Fails

**Symptoms**: Upload returns 500 error or timeout

**Solutions**:
- Check Railway logs for detailed error messages
- Verify OpenAI API key is valid and has credits
- Ensure PDF is not corrupted
- Check file size limits (Railway free tier may have limits)
- Verify database connection is working

### No Results from RAG Query

**Symptoms**: Chat returns "I don't have enough information" or empty responses

**Solutions**:
- Verify documents were successfully ingested (check Supabase `documents` table)
- Check that embeddings were created (query: `SELECT COUNT(*) FROM documents WHERE embedding IS NOT NULL;`)
- Increase `RETRIEVAL_K` value to retrieve more chunks
- Verify the query is related to uploaded document content

## Environment Variables Reference

### Backend (Railway)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | Supabase PostgreSQL connection string |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `FRONTEND_URL` | Yes | - | Vercel frontend URL for CORS |
| `EMBEDDING_MODEL` | No | `text-embedding-3-small` | OpenAI embedding model |
| `LLM_MODEL` | No | `gpt-3.5-turbo` | OpenAI LLM model |
| `EMBEDDING_DIMENSION` | No | `1536` | Vector dimension (must match model) |
| `RETRIEVAL_K` | No | `3` | Number of chunks to retrieve |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Frontend (Vercel)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | Yes | `http://localhost:8000` | Backend API URL |

## Features

- **PDF Upload**: Process PDFs in-memory (no local storage)
- **Vector Search**: Fast similarity search using pgvector HNSW index
- **Idempotent Ingestion**: Prevents duplicate document processing
- **Connection Pooling**: Efficient database connection management
- **Production Logging**: Structured logging for debugging
- **Health Checks**: `/health` endpoint for monitoring
- **Error Handling**: Comprehensive error messages and retry logic

## License

MIT
