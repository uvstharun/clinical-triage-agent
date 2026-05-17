from pydantic import BaseModel, Field
from typing import TypedDict, Optional



class PatientSymptoms(BaseModel):
    symptoms: list[str] = Field(
        description="List of symptoms the patient is experiencing"
    )
    vital_signs: dict = Field(
        description="Any vital signs mentioned — heart rate, BP, temp, O2 sat, respiratory rate"
    )
    history: list[str] = Field(
        description="Relevant medical history, medications, allergies mentioned"
    )
    onset: str = Field(
        description="When symptoms started — sudden, gradual, hours, days"
    )


class UrgencyAssessment(BaseModel):
    urgency_level: str = Field(
        description="One of exactly three values: CRITICAL, URGENT, or ROUTINE"
    )
    urgency_reasoning: str = Field(
        description="2-3 sentences explaining why this urgency level was assigned"
    )
    red_flags: list[str] = Field(
        description="Any life-threatening signs that influenced the urgency level"
    )
    recommended_timeframe: str = Field(
        description="How quickly the patient needs to be seen — immediately, within hours, within days"
    )


class ICDCoding(BaseModel):
    primary_icd_code: str = Field(
        description="The primary ICD-10-CM code for this presentation"
    )
    primary_description: str = Field(
        description="Description of the primary ICD-10 code"
    )
    additional_codes: list[str] = Field(
        description="Any additional relevant ICD-10 codes"
    )
    ccsr_category: str = Field(
        description="The CCSR category for the primary diagnosis"
    )



class TriageState(TypedDict):
    patient_description: str
    symptoms: Optional[list]
    vital_signs: Optional[dict]
    history: Optional[list]
    onset: Optional[str]
    urgency_level: Optional[str]
    urgency_reasoning: Optional[str]
    red_flags: Optional[list]
    recommended_timeframe: Optional[str]
    guidelines: Optional[str]
    primary_icd_code: Optional[str]
    primary_description: Optional[str]
    additional_codes: Optional[list]
    ccsr_category: Optional[str]
    final_report: Optional[str]