from graph import app

# -------------------------------------------------------
# THREE TEST CASES — one for each urgency path
# Critical, Urgent, and Routine
# Each should trigger a different path through the graph
# -------------------------------------------------------

CRITICAL_PATIENT = """
68-year-old male presenting with sudden onset crushing chest pain 
radiating to the left arm and jaw. Patient is diaphoretic and 
short of breath. BP 90/60, HR 118, O2 sat 88% on room air. 
History of hypertension and type 2 diabetes. Currently on 
metformin and lisinopril. Symptoms started 45 minutes ago.
"""

URGENT_PATIENT = """
45-year-old female with type 2 diabetes presenting with blood 
glucose of 380 mg/dL, increased thirst and urination for 3 days, 
mild nausea. No vomiting. Alert and oriented. BP 138/88, HR 92, 
temp 99.1F. Currently on metformin but missed doses for 2 days. 
No chest pain or shortness of breath.
"""

ROUTINE_PATIENT = """
52-year-old male with well-controlled type 2 diabetes coming in 
for routine follow-up. Last A1C was 7.1% three months ago. 
Currently on metformin 1000mg twice daily. Reports mild fatigue 
but no acute symptoms. BP 128/82, HR 74, temp 98.6F. 
Wants to discuss dietary modifications and exercise plan.
"""


def run_triage(patient_description: str, case_name: str):
    print(f"\n{'='*60}")
    print(f"CASE: {case_name}")
    print(f"{'='*60}")

    initial_state = {
        "patient_description": patient_description,
        "symptoms": None,
        "vital_signs": None,
        "history": None,
        "onset": None,
        "urgency_level": None,
        "urgency_reasoning": None,
        "red_flags": None,
        "recommended_timeframe": None,
        "guidelines": None,
        "primary_icd_code": None,
        "primary_description": None,
        "additional_codes": None,
        "ccsr_category": None,
        "final_report": None
    }

    result = app.invoke(initial_state)
    print(result["final_report"])
    print(f"\nPath taken: {result['urgency_level']}")


if __name__ == "__main__":
    # Test all three urgency paths
    run_triage(CRITICAL_PATIENT, "Critical — Chest Pain with Hemodynamic Instability")
    run_triage(URGENT_PATIENT, "Urgent — Uncontrolled Diabetes")
    run_triage(ROUTINE_PATIENT, "Routine — Diabetes Follow-up")