from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

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
