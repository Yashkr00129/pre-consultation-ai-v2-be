from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MemoCarteModel(BaseModel):
    id_memo_carte: int
    number_memo_carte: Optional[str] = None
    type_input: Optional[int] = None
    flg_verified: Optional[int] = None
    id_talk_transcribe_start: Optional[str] = None
    flg_auto_summary: Optional[int] = None
    memo_transcription_ai: Optional[str] = None
    memo_customer_ai: Optional[str] = None
    memo_service_ai: Optional[str] = None
    memo_illness_ai: Optional[str] = None
    memo_plan_ai: Optional[str] = None
    memo_prescription_ai: Optional[str] = None
    memo_other: Optional[str] = None
    id_vetty_ai: Optional[int] = None
    datetime_memo_carte: Optional[datetime] = None
    flg_delete: Optional[int] = None
    datetime_insert: Optional[datetime] = None
    datetime_update: Optional[datetime] = None
    id_clinic_id: Optional[int] = None
    id_customer_id: Optional[int] = None
    id_employee_id: Optional[int] = None
    id_employee_insert_id: Optional[int] = None
    id_employee_update_id: Optional[int] = None
    id_pet_id: Optional[int] = None
    memo_ass: Optional[str] = None
    memo_obj: Optional[str] = None
    memo_sbj: Optional[str] = None
    id_cli_common_id: Optional[int] = None
    id_request_id: Optional[int] = None
    flg_pinned: Optional[int] = None
    type_source: Optional[str] = None

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query in Japanese")
    size: Optional[int] = Field(default=10, description="Number of results to return")
    search_type: Optional[str] = Field(default="hybrid", description="Search type: vector, keyword, or hybrid")

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    took: int
    search_type: str

class IndexRequest(BaseModel):
    data: List[MemoCarteModel]




class SexEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    UNKNOWN = "Unknown"

class SpeciesEnum(str, Enum):
    DOG = "Dog"
    CAT = "Cat"
    BIRD = "Bird"
    RABBIT = "Rabbit"
    OTHER = "Other"

class ConsultationStatusEnum(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ConfidenceEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class QuestionTypeEnum(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"
    BOOLEAN = "boolean"
    SCALE = "scale"

# Pet Models
class PetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=30)
    sex: Optional[SexEnum] = None
    is_spayed: Optional[bool] = False
    breed: Optional[str] = Field(None, max_length=100)
    species: SpeciesEnum = SpeciesEnum.DOG
    weight: Optional[str] = Field(None, max_length=20)
    owner_name: Optional[str] = Field(None, max_length=100)
    owner_email: Optional[str] = Field(None, max_length=255)
    owner_phone: Optional[str] = Field(None, max_length=20)

class PetResponse(BaseModel):
    id: int
    name: str
    age: Optional[int]
    sex: Optional[str]
    is_spayed: Optional[bool]
    breed: Optional[str]
    species: str
    weight: Optional[str]
    owner_name: Optional[str]
    owner_email: Optional[str]
    owner_phone: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Consultation Models
class ExtractedKeywords(BaseModel):
    symptoms: List[str] = Field(default_factory=list, description="List of symptoms extracted from complaint")
    body_parts: List[str] = Field(default_factory=list, description="List of body parts mentioned")
    duration: List[str] = Field(default_factory=list, description="Time-related information")
    severity: List[str] = Field(default_factory=list, description="Severity indicators")
    behavioral_changes: List[str] = Field(default_factory=list, description="Changes in behavior")
    environmental_factors: List[str] = Field(default_factory=list, description="Environmental or situational factors")

class ConsultationStartRequest(BaseModel):
    pet_id: int = Field(..., description="ID of the pet for this consultation")
    initial_complaint: str = Field(..., min_length=10, max_length=2000, description="Pet owner's initial complaint")

class ConsultationStartResponse(BaseModel):
    consultation_id: int
    pet_id: int
    initial_complaint: str
    extracted_keywords: ExtractedKeywords
    complaint_category: Optional[str]
    confidence_score: Optional[ConfidenceEnum]
    suggested_questions_count: int
    status: ConsultationStatusEnum
    created_at: datetime

class QuestionResponse(BaseModel):
    question_id: int
    answer: str
    keywords_extracted: Optional[List[str]] = None

class ConsultationUpdateRequest(BaseModel):
    consultation_id: int
    question_responses: List[QuestionResponse]

class QuestionTemplateResponse(BaseModel):
    id: int
    category: str
    question_text: str
    question_type: QuestionTypeEnum
    options: Optional[List[str]]
    order_index: int
    is_required: bool
    
    class Config:
        from_attributes = True

class ConsultationResponse(BaseModel):
    id: int
    pet_id: int
    initial_complaint: str
    extracted_keywords: Optional[Dict[str, Any]]
    complaint_category: Optional[str]
    confidence_score: Optional[str]
    status: ConsultationStatusEnum
    current_question_index: int
    total_questions: int
    question_responses: Optional[Dict[str, Any]]
    preliminary_diagnosis: Optional[str]
    recommendations: Optional[Dict[str, Any]]
    retriever_results: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    pet: Optional[PetResponse]
    
    class Config:
        from_attributes = True

class KeywordExtractionResponse(BaseModel):
    extracted_keywords: ExtractedKeywords
    complaint_category: str
    confidence_score: ConfidenceEnum
    reasoning: str