#!/usr/bin/env python3
"""
Test script for the consultation API endpoints
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_consultation_workflow():
    """Test the complete consultation workflow"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🧪 Testing Vetty AI Consultation Workflow...")
        
        # Test health check
        try:
            response = await client.get(f"{base_url}/health")
            print(f"✅ Health check: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ Health check failed: {response.text}")
                return
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return
        
        # Step 1: Create a pet
        print("\n📝 Step 1: Creating a pet...")
        pet_data = {
            "name": "Buddy",
            "age": 3,
            "sex": "Male",
            "is_spayed": False,
            "breed": "Golden Retriever",
            "species": "Dog",
            "weight": "25kg",
            "owner_name": "John Smith",
            "owner_email": "john@example.com",
            "owner_phone": "+1234567890"
        }
        
        try:
            response = await client.post(f"{base_url}/api/consultation/pet", json=pet_data)
            if response.status_code == 200:
                pet_response = response.json()
                pet_id = pet_response["id"]
                print(f"✅ Pet created successfully - ID: {pet_id}, Name: {pet_response['name']}")
            else:
                print(f"❌ Pet creation failed: {response.status_code} - {response.text}")
                return
        except Exception as e:
            print(f"❌ Pet creation failed: {e}")
            return
        
        # Step 2: Start consultation with various complaint examples
        complaints = [
            "My dog has been vomiting since yesterday and won't eat his food. He seems really lethargic.",
            "My cat is losing fur around her tail and scratching constantly. The skin looks red and irritated.",
            "My dog is limping on his front right leg after our walk this morning. He whimpers when I touch it.",
            "My pet bird has been coughing and making wheezing sounds for the past 2 days.",
            "My dog ate some chocolate yesterday and now he's acting very restless and panting heavily."
        ]
        
        for i, complaint in enumerate(complaints):
            print(f"\n📋 Step 2.{i+1}: Starting consultation with complaint...")
            print(f"Complaint: '{complaint}'")
            
            consultation_request = {
                "pet_id": pet_id,
                "initial_complaint": complaint
            }
            
            try:
                response = await client.post(f"{base_url}/api/consultation/start", json=consultation_request)
                if response.status_code == 200:
                    consultation_response = response.json()
                    consultation_id = consultation_response["consultation_id"]
                    
                    print(f"✅ Consultation started - ID: {consultation_id}")
                    print(f"   Category: {consultation_response['complaint_category']}")
                    print(f"   Confidence: {consultation_response['confidence_score']}")
                    print(f"   Suggested questions: {consultation_response['suggested_questions_count']}")
                    
                    # Display extracted keywords
                    keywords = consultation_response["extracted_keywords"]
                    print(f"   Extracted keywords:")
                    for key, values in keywords.items():
                        if values:
                            print(f"     {key}: {values}")
                    
                    # Step 3: Get consultation details
                    print(f"\n📊 Step 3.{i+1}: Getting consultation details...")
                    response = await client.get(f"{base_url}/api/consultation/{consultation_id}")
                    if response.status_code == 200:
                        details = response.json()
                        print(f"✅ Consultation details retrieved")
                        print(f"   Status: {details['status']}")
                        print(f"   Created: {details['created_at']}")
                    else:
                        print(f"❌ Failed to get consultation details: {response.status_code}")
                    
                    # Step 4: Get questions for the category
                    category = consultation_response['complaint_category']
                    print(f"\n❓ Step 4.{i+1}: Getting questions for category '{category}'...")
                    response = await client.get(f"{base_url}/api/consultation/questions/category/{category}")
                    if response.status_code == 200:
                        questions = response.json()
                        print(f"✅ Found {len(questions)} questions for category '{category}'")
                        for q in questions[:2]:  # Show first 2 questions
                            print(f"   Q{q['order_index']}: {q['question_text']}")
                            if q['options']:
                                print(f"   Options: {q['options']}")
                    else:
                        print(f"❌ Failed to get questions: {response.status_code}")
                    
                    print("-" * 80)
                
                else:
                    print(f"❌ Consultation failed: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ Consultation failed: {e}")
        
        # Step 5: Get all consultations for the pet
        print(f"\n📚 Step 5: Getting all consultations for pet {pet_id}...")
        try:
            response = await client.get(f"{base_url}/api/consultation/pet/{pet_id}")
            if response.status_code == 200:
                consultations = response.json()
                print(f"✅ Found {len(consultations)} total consultations for this pet")
                for consultation in consultations:
                    print(f"   - Consultation {consultation['id']}: {consultation['complaint_category']} ({consultation['status']})")
            else:
                print(f"❌ Failed to get pet consultations: {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to get pet consultations: {e}")
        
        print("\n🎉 Consultation workflow testing completed!")

async def test_embedding_info():
    """Test the embedding configuration endpoint"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("\n🔧 Testing embedding configuration...")
        try:
            response = await client.get(f"{base_url}/api/opensearch/embedding-info")
            if response.status_code == 200:
                info = response.json()
                print(f"✅ Embedding info retrieved:")
                print(f"   Model: {info['embedding_model']}")
                print(f"   Dimension: {info['embedding_dimension']}")
                print(f"   Available indexes: {info['available_indexes']}")
            else:
                print(f"❌ Failed to get embedding info: {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to get embedding info: {e}")

if __name__ == "__main__":
    print("🚀 Starting Vetty AI Consultation API Tests...")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("=" * 80)
    
    asyncio.run(test_embedding_info())
    asyncio.run(test_consultation_workflow())