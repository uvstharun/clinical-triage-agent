import json
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from schemas import TriageState, PatientSymptoms, UrgencyAssessment, ICDCoding
from tools import search_clinical_guidelines

load_dotenv()



llm = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    max_tokens=2048
)



def build_chain(pydantic_model, system_prompt: str, human_prompt: str):
    parser = PydanticOutputParser(pydantic_object=pydantic_model)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt + "\n\n{format_instructions}"),
        ("human", human_prompt)
    ])
    return prompt | llm | parser, parser


def extract_symptoms(state: TriageState) -> dict:
    print("Node 1: Extracting symptoms...")

    chain, parser = build_chain(
        PatientSymptoms,
        """You are a clinical nurse triaging patients.
        Extract all symptoms, vital signs, medical history,
        and onset information from the patient description.
        Be thorough — missing information could affect triage decisions.
        If vital signs are not mentioned set them as empty dict.
        If history is not mentioned set it as empty list.""",
        "Patient description:\n\n{patient_description}"
    )

    result = chain.invoke({
        "patient_description": state["patient_description"],
        "format_instructions": parser.get_format_instructions()
    })

    return {
        "symptoms": result.symptoms,
        "vital_signs": result.vital_signs,
        "history": result.history,
        "onset": result.onset
    }




def assess_urgency(state: TriageState) -> dict:
    print("Node 2: Assessing urgency...")

    chain, parser = build_chain(
        UrgencyAssessment,
        """You are an experienced emergency medicine physician
        performing triage assessment.

        Use these definitions strictly:
        CRITICAL — life-threatening, needs immediate intervention
                   (chest pain with diaphoresis, stroke symptoms,
                   severe respiratory distress, altered consciousness,
                   anaphylaxis, major trauma)
        URGENT   — serious but stable, needs care within hours
                   (moderate pain, fever >103F, uncontrolled diabetes,
                   suspected fracture, severe infection)
        ROUTINE  — non-urgent, can be scheduled
                   (chronic condition follow-up, mild symptoms,
                   medication refills, routine checks)

        Be conservative — when in doubt escalate to higher urgency.""",
        """Symptoms: {symptoms}
Vital signs: {vital_signs}
Medical history: {history}
Onset: {onset}

Assess the urgency level for this patient."""
    )

    result = chain.invoke({
        "symptoms": json.dumps(state["symptoms"]),
        "vital_signs": json.dumps(state["vital_signs"]),
        "history": json.dumps(state["history"]),
        "onset": state["onset"],
        "format_instructions": parser.get_format_instructions()
    })

    return {
        "urgency_level": result.urgency_level,
        "urgency_reasoning": result.urgency_reasoning,
        "red_flags": result.red_flags,
        "recommended_timeframe": result.recommended_timeframe
    }




def search_emergency_guidelines(state: TriageState) -> dict:
    print("Node 3a: Searching emergency guidelines (CRITICAL path)...")

    query = f"emergency treatment protocols for {' '.join(state['symptoms'][:3])}"
    guidelines = search_clinical_guidelines(query, n_results=3)

    return {"guidelines": guidelines}



def search_urgent_guidelines(state: TriageState) -> dict:
    print("Node 3b: Searching urgent care guidelines (URGENT path)...")

    query = f"urgent care management of {' '.join(state['symptoms'][:3])}"
    guidelines = search_clinical_guidelines(query, n_results=3)

    return {"guidelines": guidelines}



def search_routine_guidelines(state: TriageState) -> dict:
    print("Node 3c: Searching routine guidelines (ROUTINE path)...")

    query = f"routine management and monitoring of {' '.join(state['symptoms'][:3])}"
    guidelines = search_clinical_guidelines(query, n_results=3)

    return {"guidelines": guidelines}



def generate_icd_codes(state: TriageState) -> dict:
    print("Node 4: Generating ICD codes...")

    chain, parser = build_chain(
        ICDCoding,
        """You are a clinical medical coder with expertise in ICD-10-CM.

        ICD-10-CM coding rules:
        - Code to the highest level of specificity
        - For diabetes: specify Type 1 (E10) vs Type 2 (E11) with complications
        - For hypertension with CKD: use I12 (assumes causal relationship)
        - For adverse drug effects: sequence T-code first
        - Acute vs chronic distinction matters
        - Use unspecified codes only when information is insufficient""",
        """Patient symptoms: {symptoms}
            Urgency level: {urgency_level}
            Clinical guidelines context: {guidelines}

        Suggest the most appropriate ICD-10-CM codes for this presentation."""
    )

    result = chain.invoke({
        "symptoms": json.dumps(state["symptoms"]),
        "urgency_level": state["urgency_level"],
        "guidelines": state["guidelines"][:1000] if state["guidelines"] else "No guidelines available",
        "format_instructions": parser.get_format_instructions()
    })

    return {
        "primary_icd_code": result.primary_icd_code,
        "primary_description": result.primary_description,
        "additional_codes": result.additional_codes,
        "ccsr_category": result.ccsr_category
    }



def compile_triage_report(state: TriageState) -> dict:
    print("Node 5: Compiling triage report...")

    urgency = state["urgency_level"]

    urgency_colors = {
        "CRITICAL": "CRITICAL",
        "URGENT": "URGENT",
        "ROUTINE": "ROUTINE"
    }

    report = f"""
CLINICAL TRIAGE REPORT
{'='*50}

URGENCY: {urgency_colors.get(urgency, urgency)}
TIMEFRAME: {state['recommended_timeframe']}

PRESENTING SYMPTOMS:
{chr(10).join(f'  - {s}' for s in state['symptoms'])}

VITAL SIGNS:
{chr(10).join(f'  - {k}: {v}' for k, v in state['vital_signs'].items()) if state['vital_signs'] else '  - Not documented'}

MEDICAL HISTORY:
{chr(10).join(f'  - {h}' for h in state['history']) if state['history'] else '  - Not documented'}

ONSET: {state['onset']}

TRIAGE REASONING:
  {state['urgency_reasoning']}

RED FLAGS IDENTIFIED:
{chr(10).join(f'  ⚠ {r}' for r in state['red_flags']) if state['red_flags'] else '  - None identified'}

ICD-10 CODING:
  Primary: {state['primary_icd_code']} — {state['primary_description']}
  CCSR: {state['ccsr_category']}
  Additional: {', '.join(state['additional_codes']) if state['additional_codes'] else 'None'}

CLINICAL GUIDELINES RETRIEVED:
  {state['guidelines'][:300] if state['guidelines'] else 'None'}...
"""

    return {"final_report": report}




def route_by_urgency(state: TriageState) -> str:
    urgency = state["urgency_level"].upper()
    if urgency == "CRITICAL":
        return "critical"
    elif urgency == "URGENT":
        return "urgent"
    else:
        return "routine"