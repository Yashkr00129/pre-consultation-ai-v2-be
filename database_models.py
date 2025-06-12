from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Pet(Base):
    __tablename__ = "pets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(String(10), nullable=True)  # Male/Female
    is_spayed = Column(Boolean, default=False)
    breed = Column(String(100), nullable=True)
    species = Column(String(50), nullable=False, default="Dog")  # Dog, Cat, etc.
    weight = Column(String(20), nullable=True)
    owner_name = Column(String(100), nullable=True)
    owner_email = Column(String(255), nullable=True)
    owner_phone = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with consultations
    consultations = relationship("Consultation", back_populates="pet")

class Consultation(Base):
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    
    # Initial complaint
    initial_complaint = Column(Text, nullable=False)
    
    # Extracted information
    extracted_keywords = Column(JSON, nullable=True)  # Store symptoms, body_parts, etc.
    complaint_category = Column(String(100), nullable=True)
    confidence_score = Column(String(10), nullable=True)  # Low, Medium, High
    
    # Consultation status
    status = Column(String(50), default="active")  # active, completed, cancelled
    current_question_index = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    
    # Question responses
    question_responses = Column(JSON, nullable=True)  # Store all Q&A pairs
    
    # Final diagnosis/recommendation (populated later)
    preliminary_diagnosis = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    # Retriever results
    retriever_results = Column(JSON, nullable=True)  # Results from both retrievers
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship with pet
    pet = relationship("Pet", back_populates="consultations")

class QuestionTemplate(Base):
    __tablename__ = "question_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)  # Category this question belongs to
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # multiple_choice, text, boolean, scale
    options = Column(JSON, nullable=True)  # For multiple choice questions
    order_index = Column(Integer, nullable=False)  # Order within category
    is_required = Column(Boolean, default=True)
    keywords = Column(JSON, nullable=True)  # Keywords that trigger this question
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()