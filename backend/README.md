# RAG Chatbot Backend

Production-ready FastAPI backend for the RAG chatbot. Processes PDF documents, generates embeddings, and stores them in Supabase PostgreSQL with pgvector.

## Architecture

- **Framework**: FastAPI
- **Vector Store**: Supabase PostgreSQL with pgvector extension
- **Embeddings**: OpenAI (configurable model)
- **LLM**: OpenAI GPT-3.5-turbo
- **Deployment**: Docker container on Railway

## Requirements

- Python 3.11+
- OpenAI API Key
- Supabase PostgreSQL database with pgvector extension

## Local Development Setup

### 1. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env-example` to `.env`:

```bash
cp .env-example .env
```

Edit `.env` with your values:

```env
DATABASE_URL=postgresql://user:password@host:port/database
OPENAI_API_KEY=sk-your-key-here
FRONTEND_URL=http://localhost:5173
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-3.5-turbo
EMBEDDING_DIMENSION=1536
RETRIEVAL_K=3
LOG_LEVEL=INFO
```

### 3. Set Up Supabase Database

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run the SQL script in `supabase_setup.sql` in the Supabase SQL Editor
3. Copy your database connection string to `DATABASE_URL` in `.env`

### 4. Run the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### `GET /health`

Health check endpoint for monitoring.

**Response**:
```json
{
  "status": "healthy"
}
```

### `POST /upload`

Upload and process a PDF document.

**Request**: Multipart form data with `file` field

**Response**:
```json
{
  "message": "Document 'example.pdf' processed and stored successfully (15 chunks).",
  "filename": "example.pdf"
}
```

### `POST /chat`

Query the RAG system with a question.

**Request**:
```json
{
  "query": "What is the main topic of the document?"
}
```

**Response**:
```json
{
  "response": "The main topic is..."
}
```

## Docker Development

### Build Image

```bash
docker build -t rag-backend .
```

### Run Container

```bash
docker run -p 8000:8000 --env-file .env rag-backend
```

## Production Deployment

This backend is designed for deployment on Railway using Docker.

1. Ensure `Dockerfile` and `railway.toml` are in the repository root
2. Connect your GitHub repository to Railway
3. Set all required environment variables in Railway dashboard
4. Railway will automatically build and deploy

See main [README.md](../README.md) for complete deployment instructions.

## Configuration

All configuration is managed through environment variables. See `.env-example` for all available options.

### Key Configuration Options

- **DATABASE_URL**: PostgreSQL connection string (required)
- **OPENAI_API_KEY**: OpenAI API key (required)
- **FRONTEND_URL**: Frontend URL for CORS (required)
- **EMBEDDING_MODEL**: OpenAI embedding model (default: `text-embedding-3-small`)
- **EMBEDDING_DIMENSION**: Vector dimension (default: 1536)
- **RETRIEVAL_K**: Number of chunks to retrieve (default: 3)

## Features

- **In-Memory Processing**: PDFs are processed in-memory, no local filesystem required
- **Idempotent Ingestion**: Documents are hashed to prevent duplicate processing
- **Connection Pooling**: SQLAlchemy connection pool for efficient database access
- **Structured Logging**: Production-ready logging with configurable levels
- **Error Handling**: Comprehensive error handling and user-friendly messages
- **Health Checks**: `/health` endpoint for load balancer monitoring

## Database Schema

The `documents` table structure:

- `id` (UUID): Primary key
- `content` (TEXT): Document chunk text
- `embedding` (vector): Vector embedding (dimension configurable)
- `metadata` (JSONB): Additional metadata (source, chunk_index, doc_hash, etc.)
- `source` (TEXT): Original filename
- `created_at` (TIMESTAMP): Creation timestamp

## Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` format: `postgresql://user:password@host:port/database`
- Check Supabase project is active
- Verify pgvector extension is enabled

### Embedding Errors

- Ensure `EMBEDDING_DIMENSION` matches your embedding model
- Verify OpenAI API key is valid and has credits
- Check API rate limits

### Import Errors

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.11+

## License

MIT
