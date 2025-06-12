#!/usr/bin/env python3
"""
Database initialization script for Vetty AI
Creates tables and populates sample question templates
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from database_models import create_tables, SessionLocal, QuestionTemplate
from sqlalchemy.exc import IntegrityError

def create_sample_question_templates():
    """Create sample question templates for different categories"""
    
    db = SessionLocal()
    
    sample_questions = [
        # Digestive category
        {
            "category": "digestive",
            "question_text": "How long has your pet been experiencing digestive issues?",
            "question_type": "multiple_choice",
            "options": ["Less than 24 hours", "1-3 days", "4-7 days", "More than a week"],
            "order_index": 1,
            "keywords": ["vomiting", "diarrhea", "appetite"]
        },
        {
            "category": "digestive", 
            "question_text": "What does your pet's stool look like?",
            "question_type": "multiple_choice",
            "options": ["Normal", "Loose/watery", "Hard/dry", "Contains blood", "Contains mucus"],
            "order_index": 2,
            "keywords": ["diarrhea", "stool", "bowel"]
        },
        {
            "category": "digestive",
            "question_text": "Has your pet eaten anything unusual recently?",
            "question_type": "text",
            "order_index": 3,
            "keywords": ["eating", "food", "garbage"]
        },
        
        # Respiratory category
        {
            "category": "respiratory",
            "question_text": "What type of cough does your pet have?",
            "question_type": "multiple_choice", 
            "options": ["Dry cough", "Wet/productive cough", "Honking sound", "Gagging", "No cough"],
            "order_index": 1,
            "keywords": ["cough", "coughing"]
        },
        {
            "category": "respiratory",
            "question_text": "Is your pet having difficulty breathing?",
            "question_type": "multiple_choice",
            "options": ["No difficulty", "Mild difficulty", "Moderate difficulty", "Severe difficulty"],
            "order_index": 2,
            "keywords": ["breathing", "respiratory"]
        },
        
        # Dermatological category
        {
            "category": "dermatological",
            "question_text": "Where on your pet's body is the skin issue located?",
            "question_type": "multiple_choice",
            "options": ["Face/head", "Neck", "Back", "Belly", "Legs", "Tail", "All over"],
            "order_index": 1,
            "keywords": ["skin", "fur", "hair", "rash"]
        },
        {
            "category": "dermatological",
            "question_text": "How often does your pet scratch or lick the affected area?",
            "question_type": "multiple_choice",
            "options": ["Rarely", "Occasionally", "Frequently", "Constantly"],
            "order_index": 2,
            "keywords": ["itching", "scratching", "licking"]
        },
        
        # Musculoskeletal category
        {
            "category": "musculoskeletal",
            "question_text": "Which leg or limb is affected?",
            "question_type": "multiple_choice",
            "options": ["Front left", "Front right", "Back left", "Back right", "Multiple legs", "Not sure"],
            "order_index": 1,
            "keywords": ["limping", "leg", "paw"]
        },
        {
            "category": "musculoskeletal",
            "question_text": "When did you first notice the limping?",
            "question_type": "multiple_choice",
            "options": ["Today", "Yesterday", "2-3 days ago", "This week", "Longer than a week"],
            "order_index": 2,
            "keywords": ["limping", "mobility"]
        },
        
        # Behavioral category
        {
            "category": "behavioral",
            "question_text": "How would you describe the change in your pet's behavior?",
            "question_type": "multiple_choice",
            "options": ["More aggressive", "More withdrawn", "More anxious", "Less active", "Restless", "Other"],
            "order_index": 1,
            "keywords": ["behavior", "aggressive", "anxious"]
        },
        {
            "category": "behavioral",
            "question_text": "When did you first notice these behavioral changes?",
            "question_type": "multiple_choice",
            "options": ["Today", "This week", "This month", "Gradually over time"],
            "order_index": 2,
            "keywords": ["behavioral", "changes"]
        },
        
        # Emergency category
        {
            "category": "emergency",
            "question_text": "What type of emergency situation is this?",
            "question_type": "multiple_choice",
            "options": ["Trauma/injury", "Suspected poisoning", "Difficulty breathing", "Seizure", "Severe bleeding", "Loss of consciousness", "Other"],
            "order_index": 1,
            "keywords": ["emergency", "trauma", "poisoning"]
        },
        {
            "category": "emergency",
            "question_text": "How long ago did this emergency occur?",
            "question_type": "multiple_choice",
            "options": ["Just now", "Within 1 hour", "1-3 hours ago", "3-6 hours ago", "More than 6 hours"],
            "order_index": 2,
            "keywords": ["emergency", "when"]
        },
        
        # General questions for all categories
        {
            "category": "general",
            "question_text": "Has your pet experienced this issue before?",
            "question_type": "boolean",
            "order_index": 1,
            "keywords": []
        },
        {
            "category": "general",
            "question_text": "Is your pet currently on any medications?",
            "question_type": "text",
            "order_index": 2,
            "keywords": []
        },
        {
            "category": "general",
            "question_text": "Rate your pet's overall energy level today",
            "question_type": "scale",
            "options": ["1 (Very low)", "2 (Low)", "3 (Normal)", "4 (High)", "5 (Very high)"],
            "order_index": 3,
            "keywords": []
        }
    ]
    
    try:
        for question_data in sample_questions:
            # Check if question already exists
            existing = db.query(QuestionTemplate).filter(
                QuestionTemplate.category == question_data["category"],
                QuestionTemplate.question_text == question_data["question_text"]
            ).first()
            
            if not existing:
                question = QuestionTemplate(**question_data)
                db.add(question)
        
        db.commit()
        print(f"✅ Created {len(sample_questions)} sample question templates")
        
    except Exception as e:
        print(f"❌ Error creating question templates: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Initialize database with tables and sample data"""
    print("🚀 Initializing Vetty AI Database...")
    
    try:
        # Create all tables
        create_tables()
        print("✅ Database tables created successfully")
        
        # Create sample question templates
        create_sample_question_templates()
        
        print("\n🎉 Database initialization completed!")
        print("\nNext steps:")
        print("1. Start your FastAPI server: python main.py")
        print("2. Test the API at: http://localhost:8000/docs")
        print("3. Create a pet and start a consultation using the API")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()