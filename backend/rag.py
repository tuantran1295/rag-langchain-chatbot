"""
RAG pipeline using Supabase PostgreSQL with pgvector.
Processes documents in-memory and stores embeddings in the database.
"""
import hashlib
import io
import logging
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

# Lazy-loaded globals (initialized on first use)
_embeddings = None
_llm = None
_engine = None
_settings = None


def get_settings():
    """Lazy-load settings to avoid import-time failures."""
    global _settings
    if _settings is None:
        try:
            from config import settings
            _settings = settings
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            raise RuntimeError("Configuration not loaded. Please set required environment variables.")
    return _settings


def get_embeddings():
    """Lazy-load embeddings to avoid import-time failures."""
    global _embeddings
    if _embeddings is None:
        settings = get_settings()
        _embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
    return _embeddings


def get_llm():
    """Lazy-load LLM to avoid import-time failures."""
    global _llm
    if _llm is None:
        settings = get_settings()
        _llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0,
            openai_api_key=settings.openai_api_key
        )
    return _llm


def normalize_database_url(url: str) -> str:
    """
    Normalize database URL to handle IPv6 issues and connection pooling.
    Forces IPv4 if needed and handles Supabase connection pooler.
    """
    # If it's a Supabase URL and uses IPv6, try to force IPv4
    if "supabase.co" in url:
        # Replace IPv6 hostname with IPv4 if present, or use connection pooler
        # Supabase connection pooler uses port 6543 and is better for serverless
        if ":5432" in url and "pooler" not in url:
            # Try using connection pooler instead (port 6543)
            # This is more reliable for cloud deployments
            url = url.replace(":5432", ":6543")
            # Add ?pgbouncer=true if not present
            if "?" not in url:
                url += "?pgbouncer=true"
        # Force IPv4 by using the direct connection string format
        # Remove any IPv6 addresses and use the hostname directly
        import re
        # Replace IPv6 addresses in brackets with hostname
        url = re.sub(r'\[([0-9a-fA-F:]+)\]', lambda m: url.split('@')[1].split(':')[0] if '@' in url else m.group(1), url)
    
    return url


def get_engine():
    """Lazy-load database engine to avoid import-time failures."""
    global _engine
    if _engine is None:
        settings = get_settings()
        # Normalize the connection URL to handle IPv6 and use connection pooler
        db_url = normalize_database_url(settings.database_url)
        
        # Add connection arguments to prefer IPv4
        connect_args = {}
        # Force IPv4 if possible
        if "supabase.co" in db_url:
            # Use connection pooler settings
            connect_args = {
                "connect_timeout": 10,
                "options": "-c statement_timeout=30000"
            }
        
        _engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            echo=False,
            connect_args=connect_args
        )
    return _engine


def get_vectorstore() -> PGVector:
    """
    Get or create the PGVector store with connection pooling.
    Uses the 'documents' table defined in supabase_setup.sql.
    """
    settings = get_settings()
    # Use normalized database URL (with connection pooler if Supabase)
    db_url = normalize_database_url(settings.database_url)
    return PGVector(
        embeddings=get_embeddings(),
        connection=db_url,
        collection_name="documents",
        use_jsonb=True,
        pre_delete_collection=False,  # Don't delete existing data
    )


def compute_document_hash(content: bytes) -> str:
    """
    Compute SHA256 hash of document content for idempotency.
    """
    return hashlib.sha256(content).hexdigest()


def check_document_exists(doc_hash: str) -> bool:
    """
    Check if a document with the given hash already exists in the database.
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT COUNT(*) 
                    FROM documents 
                    WHERE cmetadata->>'doc_hash' = :doc_hash
                """),
                {"doc_hash": doc_hash}
            )
            count = result.scalar()
            return count > 0
    except Exception as e:
        logger.warning(f"Error checking document existence: {e}")
        return False


def process_document(file_obj: io.BytesIO, filename: str) -> str:
    """
    Process a PDF document and store it in the vector database.
    
    Args:
        file_obj: BytesIO object containing PDF content
        filename: Original filename for metadata
    
    Returns:
        Success message
    """
    logger.info(f"Processing document: {filename}")
    
    # Read file content for hash computation
    file_obj.seek(0)
    file_content = file_obj.read()
    doc_hash = compute_document_hash(file_content)
    
    # Check if document already exists (idempotency)
    if check_document_exists(doc_hash):
        logger.info(f"Document {filename} already exists in database (hash: {doc_hash[:16]}...)")
        return f"Document '{filename}' already processed and stored."
    
    # Reset file pointer for PDF reader
    file_obj.seek(0)
    
    # 1. Load PDF from memory using pypdf directly
    pdf_reader = PdfReader(file_obj)
    docs = []
    for page_num, page in enumerate(pdf_reader.pages):
        text_content = page.extract_text()
        if text_content.strip():  # Only add non-empty pages
            docs.append(Document(
                page_content=text_content,
                metadata={"page": page_num + 1, "source": filename}
            ))
    
    if not docs:
        raise ValueError(f"No content extracted from PDF: {filename}")
    
    # 2. Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)
    
    logger.info(f"Split document into {len(splits)} chunks")
    
    # 3. Add metadata to each chunk
    # Metadata will be stored in cmetadata JSONB column
    for i, chunk in enumerate(splits):
        chunk.metadata.update({
            "source": filename,
            "chunk_index": i,
            "doc_hash": doc_hash,
            "total_chunks": len(splits)
        })
    
    # 4. Store in PGVector
    vectorstore = get_vectorstore()
    vectorstore.add_documents(splits)
    
    logger.info(f"Successfully stored {len(splits)} chunks for document: {filename}")
    return f"Document '{filename}' processed and stored successfully ({len(splits)} chunks)."


def query_rag(query_text: str) -> str:
    """
    Query the RAG system with a question.
    
    Args:
        query_text: User's question
    
    Returns:
        LLM-generated answer based on retrieved context
    """
    logger.info(f"Processing query: {query_text[:100]}...")
    
    try:
        # Load settings first
        settings = get_settings()
        
        # 1. Get vectorstore (connects to database)
        vectorstore = get_vectorstore()
        
        # 2. Create retriever with cosine similarity
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": settings.retrieval_k}
        )
        
        # 3. Create prompt template
        prompt = ChatPromptTemplate.from_template("""
        Answer the following question based only on the provided context.
        If the context does not contain enough information to answer the question,
        say that you don't have enough information.

        <context>
        {context}
        </context>

        Question: {input}
        """)
        
        # 4. Create the retrieval chain
        llm = get_llm()
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        # 5. Run query
        response = retrieval_chain.invoke({"input": query_text})
        
        logger.info("Successfully generated response")
        return response["answer"]
        
    except Exception as e:
        logger.error(f"Error in RAG query: {e}", exc_info=True)
        raise
