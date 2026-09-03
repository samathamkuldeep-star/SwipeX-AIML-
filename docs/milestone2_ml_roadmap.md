# Milestone 2 Machine Learning & NLP Transition Roadmap

**Author:** Intern 3 (AI/ML Career Intelligence)  
**Status:** Approved Architectural Roadmap  
**Target Milestone:** Milestone 2  

---

## 1. Scope Boundary Notice

> [!IMPORTANT]
> **Milestone 1 uses rule-based heuristics only (`heuristic-v0`).**  
> In compliance with the Milestone 1 SRS and project charter, no machine learning models or paid APIs are trained or deployed in Milestone 1. This document serves as the formal design plan for transitioning the heuristic stubs into a production NLP/ML architecture during Milestone 2.

---

## 2. Evolution from Heuristic to Machine Learning

```
+------------------------------------+        +----------------------------------------+
|          Milestone 1               |        |              Milestone 2               |
|      (Heuristic Engine)            |        |           (Trained NLP / ML)           |
+------------------------------------+        +----------------------------------------+
| - Regex Taxonomy Skill Extraction  |  --->  | - Fine-tuned Named Entity Recognition   |
| - Jaccard / Overlap Skill Ratio    |  --->  | - Dense Semantic Embeddings (Bi-Encoder)|
| - Bag-of-Words Description Match   |  --->  | - Cross-Encoder Relevance Re-ranking    |
| - Deterministic 0-100 Score        |  --->  | - Learning-to-Rank (LTR) on Swipes     |
+------------------------------------+        +----------------------------------------+
```

---

## 3. Core ML Components for Milestone 2

### 3.1 Dense Semantic Embeddings (Candidate-to-Job Matching)
- **Model Choice:** `sentence-transformers/all-MiniLM-L6-v2` or `BGE-small-en-v1.5` (free, open-source, sub-100ms inference).
- **Architecture:** Bi-Encoder architecture generating 384-dimensional dense vectors for resumes and job postings.
- **Vector Database:** Local `pgvector` extension in PostgreSQL or lightweight in-process vector search (e.g. FAISS / Qdrant).
- **Cosine Similarity:** Compute semantic affinity score $S_{semantic} = \cos(V_{resume}, V_{job})$.

### 3.2 Advanced Named Entity Recognition (NER) & Skill Extraction
- **Framework:** `spaCy` (e.g., `en_core_web_trf` or fine-tuned custom pipeline).
- **Entity Classes:** `SKILL`, `CERTIFICATION`, `DEGREE`, `YEARS_EXPERIENCE`, `ROLE_TITLE`.
- **Contextual Disambiguation:** Differentiating between "managed Java development" (programming language) and "traveled to Java, Indonesia" (geographical entity).

### 3.3 Two-Stage Re-Ranking Pipeline
1. **Stage 1 (Retrieval):** Fast approximate nearest neighbor (ANN) vector search to fetch top 50 candidate jobs ($<20\text{ms}$).
2. **Stage 2 (Re-ranking):** Cross-Encoder model (e.g. `cross-encoder/ms-marco-MiniLM-L-6-v2`) scoring exact pairwise interactions between candidate background and job requirements.

### 3.4 Implicit Feedback & Learning-to-Rank (LTR)
- **Signal Ingestion:** Ingest swipe interactions from Intern 2's Swipe Service:
  - Right swipe (Save / Apply) $\rightarrow$ Positive signal ($+1.0$)
  - Left swipe (Skip) $\rightarrow$ Negative signal ($0.0$)
  - Application completed $\rightarrow$ Strong positive signal ($+2.0$)
- **Model:** Gradient Boosted Trees (LightGBM / XGBoost Ranker) combining semantic similarity, salary fit, location preference, and recency decay.

---

## 4. Required Training Data & Pipeline Needs

| Data Asset | Purpose | Source / Generation Strategy |
|---|---|---|
| **Annotated Resumes** | Training custom NER skill extractors | Open-source resume datasets (e.g. Kaggle Resume Entities) + synthetic synthetic bootstrapping |
| **Job Requirement Pairs** | Fine-tuning semantic embedding models | Synthetic paired datasets generated with open-source instruction models |
| **User Swipe Telemetry** | Training LTR ranking models | Logged events from Intern 2's `/api/v1/swipes` endpoint |

---

## 5. Offline & Online Evaluation Metrics

### 5.1 Recommendation Quality Metrics
- **NDCG@10 (Normalized Discounted Cumulative Gain):** Measures ranking quality, giving higher credit to relevant jobs placed at the top of the swipe deck. Target: $\ge 0.78$.
- **MRR (Mean Reciprocal Rank):** Evaluates how quickly the first relevant job appears in the feed. Target: $\ge 0.82$.
- **Precision@K & Recall@K:** Measures the proportion of relevant jobs in the top $K=5$ and $K=10$ recommendations.

### 5.2 System Latency SLAs
- **Single Resume Parsing & Extraction:** $< 500\text{ms}$
- **Pairwise ATS Score Calculation:** $< 50\text{ms}$
- **Recommendation Feed Generation (Top 20 jobs):** $< 150\text{ms}$

---

## 6. Zero Breaking Changes Policy

Milestone 2 ML services will preserve the exact REST API schemas established in Milestone 1:
- `POST /api/v1/resume/upload` $\rightarrow$ `{ resume_id, parsed_skills[] }`
- `GET /api/v1/resume/{resume_id}/ats-score` $\rightarrow$ `{ match_score, missing_keywords[], generated_by: "ml-v1" }`
- `GET /api/v1/recommendations` $\rightarrow$ `[ { job_id, match_percentage, generated_by: "ml-v1" } ]`

This ensures that Intern 1 (API Gateway), Intern 4 (Frontend UI), and Intern 5 (QA Test Suite) can adopt the ML upgrade seamlessly by switching the `generated_by` identifier without altering client code.
