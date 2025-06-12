from models import MemoCarteModel


def combine_memo_texts(memo: MemoCarteModel) -> str:
    """Combine all memo text fields for better search"""
    text_parts = []
    
    fields_to_combine = [
        memo.memo_other,
        memo.memo_transcription_ai,
        memo.memo_customer_ai,
        memo.memo_service_ai,
        memo.memo_illness_ai,
        memo.memo_plan_ai,
        memo.memo_prescription_ai,
        memo.memo_ass,
        memo.memo_obj,
        memo.memo_sbj
    ]
    
    for field in fields_to_combine:
        if field and field.strip():
            text_parts.append(field.strip())
    
    return " ".join(text_parts)