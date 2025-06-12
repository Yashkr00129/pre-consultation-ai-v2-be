from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import logging
from datetime import datetime

from database_models import get_db, Pet, Consultation, QuestionTemplate
from models import (
    ConsultationStartRequest, 
    ConsultationStartResponse, 
    ConsultationResponse,
    PetCreate,
    PetResponse,
    QuestionTemplateResponse,
    ConsultationStatusEnum
)
from consultation_service import ConsultationService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/consultation",
    tags=["consultation"]
)

@router.post("/start", response_model=ConsultationStartResponse)
async def start_consultation(
    request: ConsultationStartRequest, 
    db: Session = Depends(get_db)
):
    """
    Start a new consultation by analyzing the initial complaint
    """
    try:
        # Verify pet exists
        pet = db.query(Pet).filter(Pet.id == request.pet_id).first()
        if not pet:
            raise HTTPException(status_code=404, detail="Pet not found")
        
        # Extract keywords and categorize complaint using OpenAI
        logger.info(f"Processing complaint for pet {request.pet_id}: {request.initial_complaint[:100]}...")
        
        analysis_result = await ConsultationService.extract_keywords_and_categorize(
            request.initial_complaint
        )
        
        # Get suggested question count for this category
        suggested_questions_count = ConsultationService.get_questions_for_category(
            analysis_result.complaint_category, 
            analysis_result.extracted_keywords
        )
        
        # Create consultation record
        consultation = Consultation(
            pet_id=request.pet_id,
            initial_complaint=request.initial_complaint,
            extracted_keywords=analysis_result.extracted_keywords.dict(),
            complaint_category=analysis_result.complaint_category,
            confidence_score=analysis_result.confidence_score.value,
            status=ConsultationStatusEnum.ACTIVE.value,
            current_question_index=0,
            total_questions=suggested_questions_count,
            question_responses={}
        )
        
        db.add(consultation)
        db.commit()
        db.refresh(consultation)
        
        logger.info(f"Created consultation {consultation.id} for pet {request.pet_id}")
        logger.info(f"Category: {analysis_result.complaint_category}, Confidence: {analysis_result.confidence_score}")
        logger.info(f"Keywords extracted: {analysis_result.extracted_keywords.dict()}")
        
        return ConsultationStartResponse(
            consultation_id=consultation.id,
            pet_id=request.pet_id,
            initial_complaint=request.initial_complaint,
            extracted_keywords=analysis_result.extracted_keywords,
            complaint_category=analysis_result.complaint_category,
            confidence_score=analysis_result.confidence_score,
            suggested_questions_count=suggested_questions_count,
            status=ConsultationStatusEnum.ACTIVE,
            created_at=consultation.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting consultation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to start consultation: {str(e)}")

@router.get("/{consultation_id}", response_model=ConsultationResponse)
async def get_consultation(consultation_id: int, db: Session = Depends(get_db)):
    """Get consultation details by ID"""
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    return consultation

@router.get("/pet/{pet_id}", response_model=List[ConsultationResponse])
async def get_pet_consultations(pet_id: int, db: Session = Depends(get_db)):
    """Get all consultations for a specific pet"""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    consultations = db.query(Consultation).filter(Consultation.pet_id == pet_id).order_by(Consultation.created_at.desc()).all()
    return consultations

@router.post("/pet", response_model=PetResponse)
async def create_pet(pet_data: PetCreate, db: Session = Depends(get_db)):
    """Create a new pet record"""
    try:
        pet = Pet(**pet_data.dict())
        db.add(pet)
        db.commit()
        db.refresh(pet)
        
        logger.info(f"Created pet {pet.id}: {pet.name}")
        return pet
        
    except Exception as e:
        logger.error(f"Error creating pet: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create pet: {str(e)}")

@router.get("/pet/{pet_id}/details", response_model=PetResponse)
async def get_pet(pet_id: int, db: Session = Depends(get_db)):
    """Get pet details by ID"""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    return pet

@router.get("/questions/category/{category}", response_model=List[QuestionTemplateResponse])
async def get_questions_by_category(category: str, db: Session = Depends(get_db)):
    """Get question templates for a specific category"""
    questions = db.query(QuestionTemplate).filter(
        QuestionTemplate.category == category
    ).order_by(QuestionTemplate.order_index).all()
    
    return questions

@router.put("/{consultation_id}/complete")
async def complete_consultation(consultation_id: int, db: Session = Depends(get_db)):
    """Mark consultation as completed"""
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    consultation.status = ConsultationStatusEnum.COMPLETED.value
    consultation.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Consultation marked as completed", "consultation_id": consultation_id}

@router.delete("/{consultation_id}")
async def cancel_consultation(consultation_id: int, db: Session = Depends(get_db)):
    """Cancel/delete a consultation"""
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    consultation.status = ConsultationStatusEnum.CANCELLED.value
    db.commit()
    
    return {"message": "Consultation cancelled", "consultation_id": consultation_id}