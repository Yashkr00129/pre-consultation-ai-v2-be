from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import uvicorn
from dotenv import load_dotenv
from openai import OpenAI
from opensearch_utils import (
    create_opensearch_client, 
    create_all_indexes,
    T_MEMO_CARTE_INDEX,
    JAPANESE_MEDICAL_DOCUMENTS_INDEX,
    get_index_info,
)
from openai_utils import get_embedding

# Import database models and create tables
from database_models import create_tables, get_db

from routers import opensearch, consultation

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Vetty AI - Pet Health Consultation API",
    description="AI-powered pet health consultation system with vector search capabilities using OpenAI Embeddings",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(opensearch.router, tags=["opensearch"])
app.include_router(consultation.router, tags=["consultation"])

# OpenAI configuration
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 1536))

# Initialize OpenSearch client using your configuration
opensearch_client = create_opensearch_client()

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Initializing Vetty AI Pet Health Consultation API...")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise RuntimeError("Failed to initialize database")
    
    # Verify OpenAI API key
    try:
        # Test OpenAI connection with a simple embedding request
        await get_embedding("test")
        logger.info(f"OpenAI API connection verified using model: {OPENAI_EMBEDDING_MODEL}")
    except Exception as e:
        logger.error(f"Failed to connect to OpenAI API: {e}")
        raise
    
    # Create all indexes
    try:
        created_indexes = create_all_indexes(opensearch_client)
        logger.info(f"OpenSearch indexes created/verified: {created_indexes}")
    except Exception as e:
        logger.error(f"Failed to create OpenSearch indexes: {e}")
        raise RuntimeError("Failed to create OpenSearch indexes")
    
    logger.info("Vetty AI Pet Health Consultation API initialized successfully")

@app.get("/")
async def root():
    return {
        "message": "Vetty AI - Pet Health Consultation API with OpenAI Embeddings",
        "status": "running",
        "embedding_model": OPENAI_EMBEDDING_MODEL,
        "embedding_dimension": EMBEDDING_DIMENSION,
        "available_indexes": [T_MEMO_CARTE_INDEX, JAPANESE_MEDICAL_DOCUMENTS_INDEX],
        "features": [
            "Pet health consultation workflow",
            "AI-powered symptom analysis", 
            "Vector-based medical document search",
            "Hybrid search capabilities",
            "Question template management"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check OpenSearch connection
        opensearch_info = opensearch_client.info()
        
        # Check OpenAI connection
        try:
            await get_embedding("health check")
            openai_status = "connected"
        except Exception as e:
            openai_status = f"error: {str(e)}"
        
        # Check database connection
        try:
            from database_models import SessionLocal
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            database_status = "connected"
        except Exception as e:
            database_status = f"error: {str(e)}"
        
        return {
            "status": "healthy",
            "opensearch": "connected",
            "opensearch_version": opensearch_info.get("version", {}).get("number", "unknown"),
            "openai": openai_status,
            "database": database_status,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)