# Clinical Triage Agent — LangGraph Multi-Path Healthcare AI

A multi-step clinical AI agent that triages patients by urgency level using LangGraph three-way conditional routing. The agent extracts symptoms, assesses urgency, searches clinical guidelines, suggests ICD codes, and compiles a structured triage report — taking a completely different path depending on whether the patient is CRITICAL, URGENT, or ROUTINE.

Built with LangGraph, LangChain, Anthropic Claude, ChromaDB, and Pydantic.

---

## What It Does

Paste a patient description and the agent runs through a graph of 7 nodes:

- CRITICAL patients get emergency protocols and immediate intervention guidance
- URGENT patients get same-day care recommendations
- ROUTINE patients get scheduled follow-up guidance

Each path searches different clinical guidelines tailored to the urgency level.

---

## Architecture

```
START
  ↓
Node 1: Extract symptoms
  ↓
Node 2: Assess urgency
  ↓
CRITICAL?        URGENT?         ROUTINE?
  ↓                ↓                ↓
Node 3a:         Node 3b:         Node 3c:
Emergency        Urgent care      Routine
guidelines       guidelines       guidelines
  ↓                ↓                ↓
Node 4: Generate ICD codes
  ↓
Node 5: Compile triage report
  ↓
END
```

The three-way conditional routing is what makes this a LangGraph agent. Each path searches clinical guidelines with a differently framed query — emergency protocols vs urgent care vs routine management.

---

## Sample Output

```
CLINICAL TRIAGE REPORT
==================================================

URGENCY: CRITICAL
TIMEFRAME: Immediately — activate emergency response

PRESENTING SYMPTOMS:
  - crushing chest pain
  - chest pain radiating to left arm and jaw
  - diaphoresis
  - shortness of breath

VITAL SIGNS:
  - blood_pressure: 90/60
  - heart_rate: 118
  - oxygen_saturation: 88% on room air

RED FLAGS:
  ⚠ Crushing chest pain with classic MI radiation pattern
  ⚠ Hypotension (90/60) suggesting cardiogenic shock
  ⚠ Hypoxia (88%) indicating pulmonary compromise
  ⚠ Tachycardia (118 bpm) with acute 45-minute onset

ICD-10: I21.9 — Acute myocardial infarction, unspecified
CCSR: Acute Myocardial Infarction
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Agent framework | LangGraph |
| LLM integration | LangChain + LangChain-Anthropic |
| LLM | Anthropic Claude (claude-haiku-4-5) |
| Vector store | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Structured outputs | Pydantic |
| Language | Python 3.13 |

---

## Key Concepts Demonstrated

**Three-way conditional routing** — after urgency assessment the graph routes to one of three nodes based on CRITICAL, URGENT, or ROUTINE classification. More realistic than binary routing for clinical triage.

**Tools inside nodes** — Nodes 3a, 3b, and 3c call the RAG tool to fetch clinical guidelines from ChromaDB before passing context to Claude. Retrieval and reasoning are separated into distinct nodes.

**State accumulation** — the TriageState TypedDict accumulates information across all 7 nodes. By Node 5 the state contains symptoms, vital signs, urgency assessment, guidelines, and ICD codes — all compiled into one report.

---

## Project Structure

```
clinical-triage-agent/
├── schemas.py          # Pydantic models + TriageState
├── tools.py            # RAG search tool (ChromaDB)
├── nodes.py            # 7 node functions + routing function
├── graph.py            # Three-way conditional graph
├── test_agent.py       # 3 test cases: critical, urgent, routine
├── requirements.txt
├── docs/               # Clinical PDFs + ChromaDB (not tracked)
├── .env                # API key (not tracked)
└── .gitignore
```

---

## How to Run It

### 1. Clone the repo
```bash
git clone https://github.com/uvstharun/clinical-triage-agent.git
cd clinical-triage-agent
```

### 2. Set up environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add your Anthropic API key
```bash
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### 4. Add clinical guidelines
Download clinical PDFs from NIH or CDC and place them in the `docs/` folder. Then build the vector store:

```bash
python -c "
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
import os

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='all-MiniLM-L6-v2'
)
client = chromadb.PersistentClient(path='docs/chroma_db')
collection = client.create_collection('clinical_guidelines', embedding_function=embedding_fn)

for filename in os.listdir('docs'):
    if filename.endswith('.pdf'):
        reader = PdfReader(f'docs/{filename}')
        text = ' '.join(page.extract_text() for page in reader.pages)
        words = text.split()
        chunks = [' '.join(words[i:i+500]) for i in range(0, len(words), 450)]
        collection.add(
            documents=chunks,
            ids=[f'{filename}_{i}' for i in range(len(chunks))],
            metadatas=[{'source': filename, 'chunk': i} for i in range(len(chunks))]
        )
        print(f'Loaded {filename} — {len(chunks)} chunks')
"
```

### 5. Run the agent
```bash
python test_agent.py
```

---

## Test Cases Included

Three synthetic patient descriptions covering all urgency paths:

**Critical** — 68-year-old with crushing chest pain, diaphoresis, BP 90/60, O2 sat 88%

**Urgent** — 45-year-old diabetic with blood glucose 380, missed medications, nausea

**Routine** — 52-year-old with well-controlled diabetes coming for follow-up

---

## Why This Project

Clinical triage is one of the highest-stakes decisions in healthcare. Getting urgency wrong delays care for critical patients or wastes resources on routine ones.

This agent demonstrates that LangGraph's conditional routing maps naturally to real clinical decision trees — the same logic emergency nurses use when triaging patients applies directly to the graph structure. CRITICAL, URGENT, and ROUTINE are not arbitrary categories — they drive different clinical protocols, different resource allocation, and different documentation requirements.

The combination of LangGraph routing, RAG-retrieved guidelines, and ICD-10 structured coding in one agent represents a realistic pattern for clinical decision support systems.

---

## Related Projects

This agent is part of a healthcare AI portfolio:

- [Healthcare NL-to-SQL Agent](https://github.com/uvstharun/healthcare-nl-sql-agent) — NL queries over 26.7M Medicare records
- [ICD Code Explainer](https://github.com/uvstharun/icd-code-explainer) — structured ICD-10 coding with Pydantic
- [Clinical Note Summarizer](https://github.com/uvstharun/clinical-note-summarizer) — LangChain discharge summary extraction
- [Job Application Agent](https://github.com/uvstharun/job-application-agent) — LangGraph fit analysis with conditional routing

---

## Author

**Vishnu Sai** — Data Scientist | Healthcare AI
[LinkedIn](https://www.linkedin.com/in/vishnusai29/) · [GitHub](https://github.com/uvstharun)