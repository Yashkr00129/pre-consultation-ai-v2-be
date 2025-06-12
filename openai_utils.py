from fastapi  import HTTPException
import logging
from openai import OpenAI
from typing import List, Optional, Dict, Any
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 1536))

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY environment variable is required")
    raise ValueError("OPENAI_API_KEY environment variable is required")
  
# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)


async def get_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI API"""
    try:
        response = openai_client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}")
      
      
      
