from langgraph.graph import StateGraph, END
from schemas import TriageState
from nodes import (
    extract_symptoms,
    assess_urgency,
    search_emergency_guidelines,
    search_urgent_guidelines,
    search_routine_guidelines,
    generate_icd_codes,
    compile_triage_report,
    route_by_urgency
)


def build_graph():
    graph = StateGraph(TriageState)
  
    graph.add_node("extract_symptoms", extract_symptoms)
    graph.add_node("assess_urgency", assess_urgency)
    graph.add_node("search_emergency_guidelines", search_emergency_guidelines)
    graph.add_node("search_urgent_guidelines", search_urgent_guidelines)
    graph.add_node("search_routine_guidelines", search_routine_guidelines)
    graph.add_node("generate_icd_codes", generate_icd_codes)
    graph.add_node("compile_triage_report", compile_triage_report)

    graph.set_entry_point("extract_symptoms")

    graph.add_edge("extract_symptoms", "assess_urgency")


    graph.add_conditional_edges(
        "assess_urgency",       # from this node
        route_by_urgency,       # call this function to decide
        {
            "critical": "search_emergency_guidelines",
            "urgent":   "search_urgent_guidelines",
            "routine":  "search_routine_guidelines"
        }
    )


    graph.add_edge("search_emergency_guidelines", "generate_icd_codes")
    graph.add_edge("search_urgent_guidelines", "generate_icd_codes")
    graph.add_edge("search_routine_guidelines", "generate_icd_codes")
    
    graph.add_edge("generate_icd_codes", "compile_triage_report")
    graph.add_edge("compile_triage_report", END)

    return graph.compile()


app = build_graph()