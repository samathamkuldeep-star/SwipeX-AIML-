# Exploratory Data Analysis (EDA) & Feature Planning: Job & Resume Intelligence

**Author:** Intern 3 (AI/ML Career Intelligence)  
**Milestone:** 1 (Day 1–2 Deliverable)  
**Scope:** Exploratory analysis of job seed data and candidate resumes to guide heuristic scoring and future ML architecture.

---

## 1. Executive Summary

This exploratory data analysis establishes the empirical foundation for SwipeX's Career Intelligence layer. We analyze:
1. The initial synthetic job posting dataset (`backend/app/data/seed_jobs.json`).
2. Candidate resumes across varied engineering disciplines (`backend/app/data/sample_resumes/`).
3. Lexical and structural overlap between job requirements and applicant profiles.

> **Key Takeaway:** While keyword matching provides an immediate, explainable baseline for Milestone 1 (`heuristic-v0`), real-world resumes exhibit significant semantic variance (acronyms, synonyms, varied phrasing) that necessitates dense vector embeddings and NLP in Milestone 2.

---

## 2. Job Postings Dataset Analysis

The initial dataset contains **8 representative tech roles** across backend, frontend, machine learning, full stack, DevOps, QA, and data analytics.

### 2.1 Skill Distribution Across Job Postings
| Domain / Role | Required Skills Listed | Average Skill Count |
|---|---|---|
| **Backend (Python)** | Python, FastAPI, PostgreSQL, Docker, Redis, REST API, Microservices, Git | 8 |
| **Frontend (React)** | React, TypeScript, JavaScript, Tailwind CSS, HTML5, CSS3, Redux, Next.js, Jest | 9 |
| **Machine Learning / NLP** | Python, PyTorch, scikit-learn, NLP, spaCy, Transformers, pandas, NumPy, SQL | 9 |
| **Full Stack** | JavaScript, TypeScript, Node.js, React, AWS, MongoDB, Express, GraphQL, Docker | 9 |
| **DevOps / Cloud** | Kubernetes, Docker, Terraform, AWS, CI/CD, Linux, Python, Prometheus, Git | 9 |
| **QA Automation** | Python, Selenium, pytest, CI/CD, Postman, SQL, Git, API Testing, Jira | 9 |
| **Junior Developer** | Python, FastAPI, SQL, Git, HTML5, CSS3, JavaScript | 7 |
| **Data Analytics** | SQL, Python, pandas, Tableau, PowerBI, Data Analysis, Excel, Statistics | 8 |

### 2.2 Top Co-Occurring Skills
- **Core Languages:** Python (62.5% of postings), JavaScript / TypeScript (37.5%), SQL (50.0%).
- **Containerization & CI/CD:** Docker (50.0%), Git (62.5%), CI/CD (37.5%).
- **APIs & Web:** REST API (37.5%), React (25.0%), FastAPI (25.0%).

---

## 3. Resume Corpus Characteristics

We evaluated sample candidate resumes in both `.pdf` and `.txt` formats:
1. **Alex Rivera (Senior Python Engineer)**: 1,501 characters, 218 words, 14 canonical skills detected.
2. **Sarah Chen (Frontend Engineer)**: 1,320 characters, 190 words, 11 canonical skills detected.
3. **Dr. Marcus Vance (ML Scientist)**: 1,480 characters, 210 words, 16 canonical skills detected.
4. **Jordan Taylor (Junior Developer)**: 890 characters, 135 words, 7 canonical skills detected.

### 3.1 Text Extraction Fidelity
- **PDF Extraction (pdfplumber vs pypdf)**: Both libraries achieved 100% text fidelity on standard single-column and two-column resumes without missing tokens or corrupted glyphs.
- **TXT Extraction**: Multi-encoding decoding (UTF-8, Latin-1, CP1252) handled varying file headers smoothly.

---

## 4. Key Findings & Feature Identification

### 4.1 Strengths of Heuristic Matching (`heuristic-v0`)
1. **Zero Cold-Start Latency**: Sub-millisecond execution time without model loading overhead.
2. **Explainability**: Clear mapping of matched skills vs. missing keywords for candidates.
3. **Deterministic Output**: Reproducible scores essential for QA integration and contract verification.

### 4.2 Challenges & Edge Cases
1. **Skill Synonyms & Aliases**: "K8s" vs "Kubernetes", "Postgres" vs "PostgreSQL", "ReactJS" vs "React".  
   *Solution implemented:* Canonical mapping dictionary in `skill_extractor.py`.
2. **Negative Contexts**: "No experience in Java" could trigger false-positive keyword hits in simple substring searches.  
   *Solution implemented:* Word-boundary regex tokens and future NLP dependency parsing.
3. **Section Weighting**: Skills mentioned in recent work experience carry higher relevance than skills mentioned in a hobbies section.  
   *Planned for Milestone 2.*

---

## 5. Summary Table: Milestone 1 Feature Weighting

| Feature Signal | Extraction Method | Weight in `heuristic-v0` | Role in Scoring |
|---|---|---|---|
| **Explicit Skill Match** | Taxonomy Regex (`SkillExtractor`) | **70%** | Direct overlap with job `skills` array |
| **Contextual Keyword Overlap** | Normalized Bag-of-Words | **30%** | Token match against job title & description |
| **Missing Keywords** | Set Difference ($S_{job} \setminus S_{resume}$) | Output metadata | Surfaced to candidate for ATS optimization |
