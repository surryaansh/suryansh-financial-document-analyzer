# Financial Document Analyzer – Debug Assignment

## Overview

This project started as a deliberately broken financial analysis system.
Agents were designed to hallucinate, fabricate investment advice, and ignore document grounding entirely.

My task was to debug it, make it reliable, and implement the bonus improvements (queue + database).

The final system is grounded, structured, and significantly more stable.

---

## What Was Broken

The original code had both deterministic bugs and prompt-level design flaws, including:

*   Agents instructed to “make up” financial advice
*   Document verifier approving everything
*   Tasks encouraging hallucinated URLs and market predictions
*   No structured JSON output
*   No grounding to actual PDF content
*   Poor separation of responsibilities

Example of Deterministic bugs:

*  llm = llm (undefined reference causing runtime failure)
*  Incorrect tool reference: FinancialDocumentTool.read_data_tool used without proper class implementation
*  Pdf(file_path=path).load() called without importing or defining Pdf
*  Invalid tool parameter tool= instead of tools= in agent definition
*  Agents configured with delegation loops that caused uncontrolled reasoning

In short, it could confidently generate fake financial analysis without reading the document.

---

## What I Changed

### 1️⃣ Rebuilt the Agent Roles

Separated responsibilities clearly:

*   **Verifier** → checks if the document contains structured financial data
*   **Financial Analyst** → retrieves and analyzes document content
*   **Risk Assessor** → evaluates risks only from extracted data
*   **Report Compiler** → produces the final structured report

This reduced cross-contamination between reasoning steps and improved reliability.

---

### 2️⃣ Implemented RAG with FAISS (Facebook AI Similarity Search)

This assignment wasn't just to debug, it was to harden it for reliability.

The original system relied entirely on the LLM’s internal knowledge.

Now the system uses the OpenAI APIs for cost-efficient, structured agent reasoning. (integrated via my existing OpenAI setup)

I implemented Retrieval-Augmented Generation (RAG):

1.  Chunk the PDF (2000 size, 200 overlap)
2.  Generate embeddings
3.  Store in FAISS
4.  Retrieve top-6 relevant chunks
5.  Force analysis strictly from retrieved content

**Why?**

Financial analysis must be document-grounded. Proper token usage is required and fabricating numbers is unacceptable.
Thus RAG pipeline was required for better optimisation.

Increasing k from 4 → 6 improved recall without increasing hallucination.

---

### 3️⃣ Tightened Prompt Engineering

Major improvements:

*   Disabled memory
*   Limited iterations
*   Enforced strict JSON-only outputs
*   Forced tool usage discipline
*   Explicitly blocked fabrication

If data is missing, the system clearly states:

> “Risk cannot be determined from the available information.”

This significantly reduced hallucinations.

---

### 4️⃣ Reduced Token Explosion (~1M Tokens Issue)

During early debugging, I hit extremely high token usage due to:

*   Loose prompts
*   Delegation loops
*   Unrestricted reasoning
*   Multiple unnecessary tool calls

**Fixes:**

*   Restricted tool calls
*   Reduced reasoning loops
*   Removed delegation
*   Enforced structured outputs

Token usage dropped from ~10–12k per run to ~6k, with more deterministic outputs.

**Big learning:** prompt discipline directly affects cost and system stability.

---

### 5️⃣ Background Queue (Bonus)

Financial analysis (embeddings + multi-agent reasoning) takes ~40–60 seconds.

Instead of blocking the API:

*   `/analyze` queues the task
*   Redis acts as broker
*   Celery processes in background
*   `/status/{task_id}` returns results

On macOS, FAISS caused SIGSEGV crashes with prefork workers.
Switching to thread pool solved it:

```bash
celery -A app.worker_tasks worker --loglevel=info --pool=threads --concurrency=4
```

### 6️⃣ MongoDB Integration (Bonus)

Each completed report is stored with:

*   file name
*   query
*   structured report JSON
*   timestamp

This allows traceability and auditability.

---

## Final Architecture

FastAPI → Redis → Celery → CrewAI Agents → FAISS (RAG) → MongoDB

## Models Used

- OpenAI GPT-4o-mini (agent reasoning)
- OpenAI text-embedding-3-small (document embeddings for RAG)

## How to Run

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Start Redis

```bash
redis-server
```

### 3️⃣ Start Celery Worker

```bash
celery -A app.worker_tasks worker --loglevel=info --pool=threads --concurrency=4
```

### 4️⃣ Start FastAPI

```bash
uvicorn app.main:app --reload
```

### 5️⃣ Use the API

*   `POST /analyze`
*   `GET /status/{task_id}`

---

## Final Result

The original system was designed to hallucinate.

The final system:

*   Is document-grounded
*   Produces structured JSON
*   Avoids fabricated financial claims
*   Handles background processing
*   Stores results persistently

It now behaves like a real financial analysis pipeline instead of a confident text generator.

## AI Usage

- Brainstorming and refining prompt structure  
- Debugging tricky issues during development  
- Improving clarity and flow of the README  
