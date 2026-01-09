import logging
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import settings
from rag import process_document, query_rag

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Chatbot API", version="1.0.0")

# CORS middleware with environment-based origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


@app.get("/health")
async def health():
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a PDF document.
    Processes file in-memory to avoid filesystem dependencies.
    """
    logger.info(f"Received upload request for file: {file.filename}")
    
    try:
        # Read file content into memory
        contents = await file.read()
        file_obj = io.BytesIO(contents)
        
        # Process document in-memory
        message = process_document(file_obj, filename=file.filename)
        logger.info(f"Successfully processed file: {file.filename}")
        return {"message": message, "filename": file.filename}
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(request: QueryRequest):
    """
    Query the RAG system with a question.
    """
    logger.info(f"Received chat query: {request.query[:100]}...")
    
    try:
        response = query_rag(request.query)
        logger.info("Successfully generated response")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)