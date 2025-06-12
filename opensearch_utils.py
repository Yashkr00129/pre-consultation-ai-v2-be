import os
from opensearchpy import OpenSearch
from dotenv import load_dotenv

load_dotenv()



# Index names
T_MEMO_CARTE_INDEX = "t_memo_carte"
JAPANESE_MEDICAL_DOCUMENTS_INDEX = "japanese_medical_documents"

# OpenSearch configuration
OPENSEARCH_ENDPOINT = os.environ.get("OPENSEARCH_ENDPOINT")
OPENSEARCH_USERNAME = os.environ.get("OPENSEARCH_USERNAME")
OPENSEARCH_PASSWORD = os.environ.get("OPENSEARCH_PASSWORD")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 1536))

def create_opensearch_client():
    """Create OpenSearch client for local or AWS instance"""
    
    # Check if we're connecting to localhost
    is_local = "localhost" in OPENSEARCH_ENDPOINT or "127.0.0.1" in OPENSEARCH_ENDPOINT
    
    if is_local:
        # Local OpenSearch configuration with SSL disabled verification
        client = OpenSearch(
            hosts=[OPENSEARCH_ENDPOINT],
            http_auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD) if OPENSEARCH_USERNAME else None,
            use_ssl=OPENSEARCH_ENDPOINT.startswith('https'),
            verify_certs=False,  # Disable certificate verification for local Docker
            ssl_assert_hostname=False,  # Don't verify hostname
            ssl_show_warn=False,  # Don't show SSL warnings
            timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )
    else:
        # AWS OpenSearch configuration
        client = OpenSearch(
            hosts=[OPENSEARCH_ENDPOINT],
            http_auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD),
            use_ssl=True,
            verify_certs=True,
            ssl_show_warn=False,
            timeout=120,
            max_retries=5,
            retry_on_timeout=True,
            http_compress=True,
            headers={"Content-Type": "application/json"}
        )
    
    return client

# Index mapping for t_memo_carte with Japanese text analysis and vector search
T_MEMO_CARTE_MAPPING = {
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "knn": True,
            "knn.algo_param.ef_search": 100,
        },
        "analysis": {
            "analyzer": {
                "japanese_analyzer": {
                    "type": "custom",
                    "tokenizer": "kuromoji_tokenizer",
                    "filter": [
                        "kuromoji_baseform",
                        "kuromoji_part_of_speech", 
                        "kuromoji_stemmer",
                        "lowercase",
                        "stop"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "id_memo_carte": {"type": "integer"},
            "number_memo_carte": {"type": "keyword"},
            "memo_other": {
                "type": "text",
                "analyzer": "japanese_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "memo_transcription_ai": {
                "type": "text",
                "analyzer": "japanese_analyzer"
            },
            "memo_customer_ai": {
                "type": "text",
                "analyzer": "japanese_analyzer"
            },
            "memo_service_ai": {
                "type": "text",
                "analyzer": "japanese_analyzer"
            },
            "memo_illness_ai": {
                "type": "text",
                "analyzer": "japanese_analyzer"
            },
            "memo_plan_ai": {
                "type": "text",
                "analyzer": "japanese_analyzer"
            },
            "memo_prescription_ai": {
                "type": "text",
                "analyzer": "japanese_analyzer"
            },
            "memo_ass": {
                "type": "text",
                "analyzer": "japanese_analyzer"
            },
            "memo_obj": {
                "type": "text",
                "analyzer": "japanese_analyzer"
            },
            "memo_sbj": {
                "type": "text",
                "analyzer": "japanese_analyzer"
            },
            "combined_memo_text": {
                "type": "text",
                "analyzer": "japanese_analyzer"
            },
            "memo_vector": {
                "type": "knn_vector",
                "dimension": EMBEDDING_DIMENSION,
                "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimil",
                    "engine": "nmslib",
                    "parameters": {
                        "ef_construction": 128,
                        "m": 24
                    }
                }
            },
            "datetime_memo_carte": {"type": "date"},
            "datetime_insert": {"type": "date"},
            "datetime_update": {"type": "date"},
            "id_clinic_id": {"type": "integer"},
            "id_customer_id": {"type": "integer"},
            "id_employee_id": {"type": "integer"},
            "id_pet_id": {"type": "integer"},
            "flg_delete": {"type": "integer"},
            "flg_verified": {"type": "integer"},
            "flg_pinned": {"type": "integer"},
            "type_source": {"type": "keyword"}
        }
    }
}

# Index mapping for japanese_medical_documents
JAPANESE_MEDICAL_DOCUMENTS_MAPPING = {
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "knn": True,
            "knn.algo_param.ef_search": 100,
        },
        "analysis": {
            "analyzer": {
                "japanese_medical_analyzer": {
                    "type": "custom",
                    "tokenizer": "kuromoji_tokenizer",
                    "filter": [
                        "kuromoji_baseform",
                        "kuromoji_part_of_speech",
                        "kuromoji_stemmer",
                        "lowercase",
                        "stop"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "document_id": {"type": "keyword"},
            "title": {
                "type": "text",
                "analyzer": "japanese_medical_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "content": {
                "type": "text",
                "analyzer": "japanese_medical_analyzer"
            },
            "summary": {
                "type": "text",
                "analyzer": "japanese_medical_analyzer"
            },
            "medical_terms": {
                "type": "text",
                "analyzer": "japanese_medical_analyzer"
            },
            "category": {"type": "keyword"},
            "subcategory": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "document_vector": {
                "type": "knn_vector",
                "dimension": EMBEDDING_DIMENSION,
                "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimil",
                    "engine": "nmslib",
                    "parameters": {
                        "ef_construction": 128,
                        "m": 24
                    }
                }
            },
            "combined_text": {
                "type": "text",
                "analyzer": "japanese_medical_analyzer"
            },
            "source": {"type": "keyword"},
            "author": {"type": "keyword"},
            "date_created": {"type": "date"},
            "date_updated": {"type": "date"},
            "version": {"type": "keyword"},
            "language": {"type": "keyword"},
            "confidence_score": {"type": "float"},
            "is_active": {"type": "boolean"}
        }
    }
}

def create_index(client, index_name: str, mapping: dict):
    """Create an OpenSearch index with the specified mapping"""
    try:
        if client.indices.exists(index=index_name):
            print(f"Index {index_name} already exists")
            return True
        
        response = client.indices.create(
            index=index_name,
            body=mapping
        )
        print(f"Created index {index_name}: {response}")
        return True
    except Exception as e:
        print(f"Error creating index {index_name}: {e}")
        return False

def create_all_indexes(client):
    """Create all required indexes"""
    indexes_created = []
    
    # Create t_memo_carte index
    if create_index(client, T_MEMO_CARTE_INDEX, T_MEMO_CARTE_MAPPING):
        indexes_created.append(T_MEMO_CARTE_INDEX)
    
    # Create japanese_medical_documents index
    if create_index(client, JAPANESE_MEDICAL_DOCUMENTS_INDEX, JAPANESE_MEDICAL_DOCUMENTS_MAPPING):
        indexes_created.append(JAPANESE_MEDICAL_DOCUMENTS_INDEX)
    
    return indexes_created

def delete_index(client, index_name: str):
    """Delete an OpenSearch index"""
    try:
        if not client.indices.exists(index=index_name):
            return {"message": f"Index {index_name} does not exist"}
        
        response = client.indices.delete(index=index_name)
        return {"message": f"Index {index_name} deleted successfully", "response": response}
    except Exception as e:
        return {"error": f"Failed to delete index {index_name}: {str(e)}"}

def get_index_info(client, index_name: str):
    """Get information about an index"""
    try:
        if not client.indices.exists(index=index_name):
            return {"error": f"Index {index_name} does not exist"}
        
        stats = client.indices.stats(index=index_name)
        mapping = client.indices.get_mapping(index=index_name)
        
        return {
            "exists": True,
            "doc_count": stats["indices"][index_name]["total"]["docs"]["count"],
            "store_size": stats["indices"][index_name]["total"]["store"]["size_in_bytes"],
            "mapping": mapping[index_name]["mappings"]
        }
    except Exception as e:
        return {"error": f"Failed to get info for index {index_name}: {str(e)}"}
    
    
opensearch_client = create_opensearch_client()

if __name__ == "__main__":
    # Test the OpenSearch client and create indexes
    client = create_opensearch_client()
    created_indexes = create_all_indexes(client)
    print(f"Created indexes: {created_indexes}")