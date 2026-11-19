# Inkloom AI — Intelligent Brand Governance Platform

> **Intelligent Brand Governance Platform.** Maintain consistent, accurate, and trustworthy brand communication across all marketing, legal, technical, and corporate channels.

---

## 1. Executive Overview

Inkloom AI is an enterprise SaaS platform engineered to solve brand fragmentation, unverified claims, and terminology drift. Rather than acting as a generic content generator or spell-checker, Inkloom AI acts as an authoritative governance gatekeeper:

- **Store Authoritative Brand Truth:** Manage brand guidelines, approved corporate facts & metrics, official product terminology, and restricted marketing phrases.
- **Evidence-Backed Inspection:** Automatically inspect drafts against stored brand policies and certified facts. Every violation cites the exact source document, chapter, or audited benchmark.
- **Intent-Preserving Smart Correction:** Recommend focused sentence replacements that preserve the author's core value proposition and tone while removing prohibited terms or hyperbole.
- **Human Reviewer Sign-Off:** Reviewers retain final publication sign-off authority with complete revision history and immutable audit trails.

---

## 2. Core Innovations

### A. Evidence-Backed AI Detection
- Identifies problematic text and exact character spans for visual highlighting.
- Explains why content violates governance guidelines.
- Cites the specific supporting brand document, section, or corporate fact.
- Categorises findings: `terminology`, `restricted_phrase`, `unsupported_claim`, `tone_inconsistency`, `guideline_violation`.
- Assigns severity: `critical`, `high`, `medium`, `low`, `info`.
- Marks unsupported claims as unverified when no factual record exists.
- **Guaranteed zero fabrication:** Every citation is grounded in database records.

### B. Intent-Preserving Smart Correction
- Identifies the exact surrounding sentence.
- Generates a focused, brand-compliant replacement.
- Preserves the original message meaning and tone without introducing unverified claims.
- Displays side-by-side original and suggested versions.
- Supports accepting, rejecting, or manually customising suggestions.
- Automatically saves persistent revisions upon acceptance without silent overwrites.

### C. Brand Governance Intelligence
- Aggregates recurring terminology drift, prohibited phrase usage, and unsupported claims.
- Computes overall Brand Adherence Score.
- Generates actionable governance recommendations based on real historical data.
- Tracks audit trails of review attestations and content modifications.

---

## 3. Technology Stack

- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Lucide React, React Router v6, Axios
- **Backend:** Python 3.10+, FastAPI, SQLAlchemy 2.0 ORM, Pydantic v2, Alembic, HTTPX
- **Database:** Render PostgreSQL (with pgvector support & SQLite fallback for local development)
- **AI Engine:** NVIDIA Nemotron via OpenRouter (`nvidia/llama-3.1-nemotron-70b-instruct`) + Deterministic Rule Engine
- **Document Processing:** PyMuPDF, python-docx, Pillow

---

## 4. Quick Demo Access (For Reviewers & Judges)

The application includes a preloaded enterprise demo organisation: **Aura Global Technologies**.

On the login page, you can use the **1-Click Instant Demo Access** buttons:
- **Lead Reviewer:** `reviewer@inkloom.ai` (Password: `demo1234`) — Full review & approval authority.
- **Content Strategist:** `creator@inkloom.ai` (Password: `demo1234`) — Draft submission & revision authority.

---

## 5. Local Development Setup

### Backend Setup
```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Set your OPENROUTER_API_KEY and DATABASE_URL in .env

# Run server
uvicorn app.main:app --reload --port 8000
```
Swagger API documentation will be available at: `http://localhost:8000/docs`

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
Frontend will be running at: `http://localhost:5173`

---

## 6. End-to-End User Journey

1. Open Inkloom AI at `http://localhost:5173`.
2. Click **Lead Reviewer** or **Content Strategist** for 1-click access.
3. Explore the **Brand Knowledge Base** to inspect guidelines, approved facts, and terminology rules.
4. Go to **Content Analysis Workspace** and click **Load Financial Press Release**.
5. Click **Inspect Brand Governance** to run deterministic matching and evidence retrieval.
6. Review highlighted findings, severity levels, and evidence citations on the **Analysis Results** page.
7. Click **Open Smart Correction Editor** to review intent-preserving suggestions.
8. Accept or customise corrections and observe automatic revision creation.
9. Click **Submit for Review**.
10. Open **Review Centre** as Reviewer to sign off or request changes.
11. View updated trends and recommendations in **Governance Analytics**.

---

## 7. Deployment Configuration

### Render (Backend & Database)
- **Service Type:** Web Service
- **Build Command:** `pip install -r backend/requirements.txt`
- **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  - `DATABASE_URL`: Render PostgreSQL connection string
  - `SECRET_KEY`: Secure random key
  - `OPENROUTER_API_KEY`: OpenRouter API key
  - `NEMOTRON_MODEL`: `nvidia/llama-3.1-nemotron-70b-instruct`
  - `FRONTEND_URL`: Vercel frontend URL

### Vercel (Frontend)
- **Framework Preset:** Vite
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Environment Variables:**
  - `VITE_API_URL`: Render backend public URL (e.g. `https://inkloom-api.onrender.com/api/v1`)
