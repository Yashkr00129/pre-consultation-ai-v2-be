import json
import logging
from typing import Dict, Any
from openai import OpenAI
from models import ExtractedKeywords, ConfidenceEnum, KeywordExtractionResponse
import os

logger = logging.getLogger(__name__)

# OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ConsultationService:
    
    CATEGORY_MAPPING = {
        "digestive": ["vomiting", "diarrhea", "constipation", "loss of appetite", "stomach", "intestinal", "nausea", "bloating"],
        "respiratory": ["coughing", "breathing difficulty", "wheezing", "sneezing", "nose", "chest", "lungs", "throat"],
        "dermatological": ["skin", "fur", "hair loss", "itching", "rash", "allergies", "scratching", "scales"],
        "musculoskeletal": ["limping", "joint pain", "muscle", "bone", "leg", "hip", "back", "mobility"],
        "neurological": ["seizures", "tremors", "coordination", "balance", "head", "brain", "nervous"],
        "urinary": ["urination", "bladder", "kidney", "urine", "frequency", "blood in urine"],
        "behavioral": ["aggression", "anxiety", "depression", "behavioral changes", "restlessness", "lethargy"],
        "ophthalmologic": ["eye", "vision", "discharge", "redness", "squinting", "blindness"],
        "otic": ["ear", "hearing", "discharge", "odor", "scratching ears", "head shaking"],
        "dental": ["teeth", "gums", "mouth", "bad breath", "chewing difficulty", "oral"],
        "reproductive": ["pregnancy", "heat", "breeding", "reproductive", "genital"],
        "emergency": ["trauma", "poisoning", "severe pain", "unconscious", "bleeding", "accident"]
    }

    @staticmethod
    async def extract_keywords_and_categorize(complaint: str) -> KeywordExtractionResponse:
        """Extract keywords and categorize the complaint using OpenAI"""
        
        prompt = f"""
        As a veterinary AI assistant, analyze the following pet owner's complaint and extract relevant information.

        Pet Owner's Complaint: "{complaint}"

        Please extract and categorize the following information in JSON format:

        1. **symptoms**: List of specific symptoms mentioned (e.g., vomiting, diarrhea, lethargy)
        2. **body_parts**: List of body parts or areas mentioned (e.g., tail, leg, stomach, eyes)
        3. **duration**: Time-related information (e.g., "since yesterday", "for 3 days", "suddenly")
        4. **severity**: Severity indicators (e.g., "severe", "mild", "getting worse", "occasional")
        5. **behavioral_changes**: Changes in behavior (e.g., "not eating", "hiding", "more aggressive")
        6. **environmental_factors**: Environmental or situational factors (e.g., "after eating", "when walking", "at night")

        Also determine:
        - **category**: The most appropriate medical category from: digestive, respiratory, dermatological, musculoskeletal, neurological, urinary, behavioral, ophthalmologic, otic, dental, reproductive, emergency
        - **confidence**: Your confidence level in the categorization (Low, Medium, High)
        - **reasoning**: Brief explanation of your categorization

        Respond in this exact JSON format:
        {{
            "extracted_keywords": {{
                "symptoms": ["symptom1", "symptom2"],
                "body_parts": ["part1", "part2"],
                "duration": ["duration1"],
                "severity": ["severity1"],
                "behavioral_changes": ["change1", "change2"],
                "environmental_factors": ["factor1"]
            }},
            "complaint_category": "category_name",
            "confidence_score": "High|Medium|Low",
            "reasoning": "Brief explanation of why this category was chosen"
        }}
        """

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a veterinary AI assistant specialized in analyzing pet health complaints. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse the JSON response
            try:
                parsed_response = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed_response = json.loads(json_match.group())
                else:
                    raise ValueError("Could not extract valid JSON from OpenAI response")
            
            # Validate and create response
            extracted_keywords = ExtractedKeywords(**parsed_response["extracted_keywords"])
            
            return KeywordExtractionResponse(
                extracted_keywords=extracted_keywords,
                complaint_category=parsed_response["complaint_category"],
                confidence_score=ConfidenceEnum(parsed_response["confidence_score"]),
                reasoning=parsed_response["reasoning"]
            )
            
        except Exception as e:
            logger.error(f"Error in keyword extraction: {e}")
            
            # Fallback: Simple keyword matching
            return ConsultationService._fallback_keyword_extraction(complaint)
    
    @staticmethod
    def _fallback_keyword_extraction(complaint: str) -> KeywordExtractionResponse:
        """Fallback method for keyword extraction using simple pattern matching"""
        complaint_lower = complaint.lower()
        
        # Simple keyword extraction
        symptoms = []
        body_parts = []
        duration = []
        severity = []
        behavioral_changes = []
        environmental_factors = []
        
        # Common symptoms
        symptom_keywords = ["vomiting", "diarrhea", "coughing", "sneezing", "itching", "limping", "bleeding", "swelling", "discharge"]
        for keyword in symptom_keywords:
            if keyword in complaint_lower:
                symptoms.append(keyword)
        
        # Common body parts
        body_part_keywords = ["tail", "leg", "eye", "ear", "mouth", "nose", "stomach", "back", "paw", "head"]
        for keyword in body_part_keywords:
            if keyword in complaint_lower:
                body_parts.append(keyword)
        
        # Duration indicators
        duration_keywords = ["yesterday", "today", "days", "weeks", "hours", "suddenly", "gradually"]
        for keyword in duration_keywords:
            if keyword in complaint_lower:
                duration.append(keyword)
        
        # Behavioral changes
        behavior_keywords = ["not eating", "hiding", "aggressive", "lethargic", "restless"]
        for keyword in behavior_keywords:
            if keyword in complaint_lower:
                behavioral_changes.append(keyword)
        
        # Determine category based on keywords
        category = "general"
        confidence = ConfidenceEnum.LOW
        
        for cat, keywords in ConsultationService.CATEGORY_MAPPING.items():
            for keyword in keywords:
                if keyword in complaint_lower:
                    category = cat
                    confidence = ConfidenceEnum.MEDIUM
                    break
            if category != "general":
                break
        
        return KeywordExtractionResponse(
            extracted_keywords=ExtractedKeywords(
                symptoms=symptoms,
                body_parts=body_parts,
                duration=duration,
                severity=severity,
                behavioral_changes=behavioral_changes,
                environmental_factors=environmental_factors
            ),
            complaint_category=category,
            confidence_score=confidence,
            reasoning="Fallback analysis using pattern matching"
        )
    
    @staticmethod
    def get_questions_for_category(category: str, extracted_keywords: ExtractedKeywords) -> int:
        """Get the number of questions for a given category"""
        # This would typically query your question templates from the database
        # For now, return a default number based on category
        question_counts = {
            "digestive": 8,
            "respiratory": 6,
            "dermatological": 7,
            "musculoskeletal": 5,
            "neurological": 9,
            "urinary": 6,
            "behavioral": 8,
            "ophthalmologic": 5,
            "otic": 4,
            "dental": 5,
            "reproductive": 6,
            "emergency": 10,
            "general": 12
        }
        return question_counts.get(category, 10)