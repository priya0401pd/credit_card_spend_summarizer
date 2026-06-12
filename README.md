Streamlit UI
     ↓
FastAPI
     ↓
LangGraph
     ↓
Query Router
     ↓
 ┌─────────────┬─────────────┐
 │             │             │
SQL Agent   RAG Agent   Hybrid Agent
 │             │             │
Postgres    PGVector    Both
 │             │             │
 └─────────────┴─────────────┘
              ↓
           GPT/Gemini
              ↓
          Response

PDF
 ↓
Parsed
 ↓
Chunked
 ↓
Embedded
 ↓
Stored
 ↓
103 chunks

uv add guardrails-ai
guardrails hub install hub://guardrails/toxic_language
guardrails hub install hub://guardrails/guardrails_pii