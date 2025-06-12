# setup.py
import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def setup_project():
    """Setup the memo carte retriever project"""
    print("🚀 Setting up Memo Carte Retriever API...")
    
    # Create necessary directories
    directories = ["alembic/versions", "logs", "tests"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Initialize Alembic if not already done
    if not Path("alembic").exists():
        run_command("pipenv run alembic init alembic", "Initializing Alembic")
    
    # Create initial migration
    run_command("pipenv run alembic revision --autogenerate -m 'Initial migration'", "Creating initial migration")
    
    # Apply migrations
    run_command("pipenv run alembic upgrade head", "Applying database migrations")
    
    print("\n🎉 Setup completed! You can now:")
    print("1. Start the development services: docker-compose up -d")
    print("2. Run the API server: pipenv run uvicorn main:app --reload")
    print("3. Access the API docs at: http://localhost:8000/docs")
    print("4. Access OpenSearch Dashboards at: http://localhost:5601")

if __name__ == "__main__":
    setup_project()

# test_api.py
import httpx
import asyncio
import json
from datetime import datetime

async def test_api():
    """Test the memo carte API endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🧪 Testing Memo Carte Retriever API...")
        
        # Test health check
        try:
            response = await client.get(f"{base_url}/health")
            print(f"✅ Health check: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return
        
        # Test sample data indexing
        sample_memo = {
            "data": [
                {
                    "id_memo_carte": 1,
                    "number_memo_carte": "TEST001",
                    "memo_other": "患者の犬が咳をしており、食欲不振の症状があります。体温は38.5度で、やや高めです。",
                    "memo_transcription_ai": "飼い主が心配そうに話している。犬の症状について詳しく説明。",
                    "memo_illness_ai": "呼吸器系の疾患の可能性があります。風邪または気管支炎の疑い。",
                    "memo_plan_ai": "抗生物質の投与を検討。3日後の再診を予定。",
                    "datetime_memo_carte": datetime.now().isoformat(),
                    "flg_delete": 0,
                    "id_clinic_id": 1,
                    "id_customer_id": 1,
                    "id_pet_id": 1
                }
            ]
        }
        
        try:
            response = await client.post(f"{base_url}/index", json=sample_memo)
            print(f"✅ Sample data indexing: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ Sample data indexing failed: {e}")
        
        # Wait a moment for indexing to complete
        await asyncio.sleep(2)
        
        # Test vector search
        search_queries = [
            {"query": "咳", "search_type": "vector", "size": 5},
            {"query": "犬の病気", "search_type": "keyword", "size": 5},
            {"query": "呼吸器", "search_type": "hybrid", "size": 5}
        ]
        
        for search_query in search_queries:
            try:
                response = await client.post(f"{base_url}/search", json=search_query)
                result = response.json()
                print(f"✅ {search_query['search_type'].upper()} search for '{search_query['query']}': {response.status_code}")
                print(f"   Found {result.get('total', 0)} results in {result.get('took', 0)}ms")
                if result.get('results'):
                    print(f"   Top result score: {result['results'][0].get('score', 0):.4f}")
            except Exception as e:
                print(f"❌ {search_query['search_type']} search failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())