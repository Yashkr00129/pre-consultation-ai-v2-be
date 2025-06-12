from fastapi import APIRouter,HTTPException
from typing import List, Optional, Dict, Any
import os
import datetime
import logging

from utils import combine_memo_texts
from openai_utils import get_embedding
from opensearch_utils import (
    create_opensearch_client, 
    create_all_indexes,
    opensearch_client,
    T_MEMO_CARTE_INDEX,
    JAPANESE_MEDICAL_DOCUMENTS_INDEX,
    get_index_info,
    delete_index
)
from models import IndexRequest,SearchRequest,SearchResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
  prefix="/api/opensearch"
)

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 1536))


@router.get("/embedding-info")
async def get_embedding_info():
    """Get information about the current embedding configuration"""
    return {
        "embedding_model": OPENAI_EMBEDDING_MODEL,
        "embedding_dimension": EMBEDDING_DIMENSION,
        "available_indexes": [T_MEMO_CARTE_INDEX, JAPANESE_MEDICAL_DOCUMENTS_INDEX],
        "opensearch_endpoint": os.getenv("OPENSEARCH_ENDPOINT")
    }


@router.get("/indexes")
async def list_indexes():
    """List all available indexes and their information"""
    try:
        indexes_info = {
            "t_memo_carte": get_index_info(opensearch_client, T_MEMO_CARTE_INDEX),
            "japanese_medical_documents": get_index_info(opensearch_client, JAPANESE_MEDICAL_DOCUMENTS_INDEX)
        }
        return {
            "available_indexes": [T_MEMO_CARTE_INDEX, JAPANESE_MEDICAL_DOCUMENTS_INDEX],
            "indexes_info": indexes_info
        }
    except Exception as e:
        logger.error(f"Error listing indexes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list indexes: {str(e)}")
      
      
      
@router.get("/index/{index_name}/info")
async def get_opensearch_index_info(index_name: str):
    """Get information about an OpenSearch index"""
    try:
        # Validate index name
        valid_indexes = [T_MEMO_CARTE_INDEX, JAPANESE_MEDICAL_DOCUMENTS_INDEX]
        if index_name not in valid_indexes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid index name. Valid indexes: {valid_indexes}"
            )
        
        result = get_index_info(opensearch_client, index_name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting index info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get index info: {str(e)}")

@router.delete("/index/{index_name}")
async def delete_opensearch_index(index_name: str):
    """Delete an OpenSearch index"""
    try:
        # Validate index name
        valid_indexes = [T_MEMO_CARTE_INDEX, JAPANESE_MEDICAL_DOCUMENTS_INDEX]
        if index_name not in valid_indexes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid index name. Valid indexes: {valid_indexes}"
            )
        
        result = delete_index(opensearch_client, index_name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting index: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete index: {str(e)}")


@router.post("/index", response_model=Dict[str, Any])
async def index_memo_carte_data(request: IndexRequest):
    """Index memo carte data to OpenSearch with OpenAI vector embeddings"""
    try:
        indexed_count = 0
        errors = []
        
        for memo in request.data:
            try:
                # Combine memo texts for vectorization
                combined_text = combine_memo_texts(memo)
                
                # Generate vector embedding if there's text content
                memo_vector = None
                if combined_text.strip():
                    memo_vector = await get_embedding(combined_text)
                    logger.info(f"Generated embedding for memo {memo.id_memo_carte} with {len(combined_text)} characters")
                
                # Prepare document for indexing
                doc = {
                    **memo.dict(),
                    "combined_memo_text": combined_text,
                    "memo_vector": memo_vector
                }
                
                # Convert datetime objects to ISO format strings
                for field in ["datetime_memo_carte", "datetime_insert", "datetime_update"]:
                    if doc.get(field):
                        doc[field] = doc[field].isoformat() if isinstance(doc[field], datetime) else doc[field]
                
                # Index document to t_memo_carte index
                response = opensearch_client.index(
                    index=T_MEMO_CARTE_INDEX,
                    id=memo.id_memo_carte,
                    body=doc
                )
                
                if response.get("result") in ["created", "updated"]:
                    indexed_count += 1
                    logger.info(f"Successfully indexed memo {memo.id_memo_carte}")
                else:
                    errors.append(f"Failed to index memo {memo.id_memo_carte}: {response}")
                    
            except Exception as e:
                errors.append(f"Error processing memo {memo.id_memo_carte}: {str(e)}")
                logger.error(f"Error indexing memo {memo.id_memo_carte}: {e}")
        
        # Refresh index to make documents searchable
        opensearch_client.indices.refresh(index=T_MEMO_CARTE_INDEX)
        
        return {
            "message": f"Indexing completed using {OPENAI_EMBEDDING_MODEL}",
            "indexed_count": indexed_count,
            "total_requested": len(request.data),
            "embedding_model": OPENAI_EMBEDDING_MODEL,
            "embedding_dimension": EMBEDDING_DIMENSION,
            "errors": errors[:10] if errors else []
        }
        
    except Exception as e:
        logger.error(f"Error during indexing: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_memo_carte(request: SearchRequest):
    """Perform vector, keyword, or hybrid search on memo carte data using OpenAI embeddings"""
    try:
        if request.search_type == "vector":
            # Pure vector search using OpenAI embeddings
            query_vector = await get_embedding(request.query)
            logger.info(f"Generated query embedding for: {request.query}")
            
            search_body = {
                "size": request.size,
                "query": {
                    "knn": {
                        "memo_vector": {
                            "vector": query_vector,
                            "k": request.size
                        }
                    }
                },
                "_source": {
                    "excludes": ["memo_vector"]
                }
            }
            
        elif request.search_type == "keyword":
            # Pure keyword search with Japanese analyzer
            search_body = {
                "size": request.size,
                "query": {
                    "multi_match": {
                        "query": request.query,
                        "fields": [
                            "combined_memo_text^2",
                            "memo_other^1.5",
                            "memo_transcription_ai",
                            "memo_customer_ai",
                            "memo_service_ai",
                            "memo_illness_ai",
                            "memo_plan_ai",
                            "memo_prescription_ai",
                            "memo_ass",
                            "memo_obj",
                            "memo_sbj"
                        ],
                        "type": "best_fields",
                        "analyzer": "japanese_analyzer"
                    }
                },
                "_source": {
                    "excludes": ["memo_vector"]
                }
            }
            
        else:  # hybrid search (default)
            # Hybrid search combining OpenAI vector and keyword search
            query_vector = await get_embedding(request.query)
            logger.info(f"Generated query embedding for hybrid search: {request.query}")
            
            search_body = {
                "size": request.size,
                "query": {
                    "bool": {
                        "should": [
                            {
                                "knn": {
                                    "memo_vector": {
                                        "vector": query_vector,
                                        "k": request.size,
                                        "boost": 1.2
                                    }
                                }
                            },
                            {
                                "multi_match": {
                                    "query": request.query,
                                    "fields": [
                                        "combined_memo_text^2",
                                        "memo_other^1.5",
                                        "memo_transcription_ai",
                                        "memo_customer_ai",
                                        "memo_service_ai",
                                        "memo_illness_ai",
                                        "memo_plan_ai",
                                        "memo_prescription_ai",
                                        "memo_ass",
                                        "memo_obj",
                                        "memo_sbj"
                                    ],
                                    "type": "best_fields",
                                    "analyzer": "japanese_analyzer",
                                    "boost": 0.8
                                }
                            }
                        ],
                        "minimum_should_match": 1
                    }
                },
                "_source": {
                    "excludes": ["memo_vector"]
                }
            }
        
        # Add filter for non-deleted records
        if "query" in search_body and "bool" not in search_body["query"]:
            search_body["query"] = {
                "bool": {
                    "must": [search_body["query"]],
                    "filter": [
                        {"term": {"flg_delete": 0}}
                    ]
                }
            }
        elif "query" in search_body and "bool" in search_body["query"]:
            if "filter" not in search_body["query"]["bool"]:
                search_body["query"]["bool"]["filter"] = []
            search_body["query"]["bool"]["filter"].append({"term": {"flg_delete": 0}})
        
        # Execute search on t_memo_carte index
        response = opensearch_client.search(
            index=T_MEMO_CARTE_INDEX,
            body=search_body
        )
        
        # Format results
        results = []
        for hit in response["hits"]["hits"]:
            result = {
                "id": hit["_id"],
                "score": hit["_score"],
                "source": hit["_source"]
            }
            results.append(result)
        
        logger.info(f"Search completed: {len(results)} results for '{request.query}' using {request.search_type}")
        
        return SearchResponse(
            results=results,
            total=response["hits"]["total"]["value"],
            took=response["took"],
            search_type=request.search_type
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

