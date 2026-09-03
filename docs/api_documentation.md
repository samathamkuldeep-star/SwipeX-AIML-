# SwipeX Career Intelligence API Documentation & Integration Guide

**Service Owner:** Intern 3 (AI/ML Career Intelligence)  
**Milestone:** 1  
**Base URL:** `http://localhost:8000/api/v1`  
**Swagger UI:** `http://localhost:8000/docs`  
**ReDoc:** `http://localhost:8000/redoc`  

---

## 1. Quickstart & Local Setup

### 1.1 Prerequisites
- Python 3.10+ (Tested on Python 3.11–3.14)
- Virtual environment (`venv`)

### 1.2 Installation
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 1.3 Running the Service
```bash
# Launch FastAPI development server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 1.4 Running the Test Suite
```bash
# Execute automated tests with pytest
pytest backend/tests/ -v

# Run code style & lint checks
ruff check backend/
```

---

## 2. Frozen API Endpoints (SRS Section 7.3)

### 2.1 Upload Resume
* **Endpoint:** `POST /api/v1/resume/upload`
* **Content-Type:** `multipart/form-data`
* **Parameters:**
  * `file` *(required, binary)*: Resume file (`.pdf` or `.txt`, max 10 MB).
  * `user_id` *(optional, string in form body)*: Associated user identifier.
  * `X-User-ID` *(optional, string in header)*: Gateway-forwarded user identifier.

#### Request Example (cURL):
```bash
curl -X POST "http://localhost:8000/api/v1/resume/upload" \
  -H "X-User-ID: user_12345" \
  -F "file=@backend/app/data/sample_resumes/resume_backend_alex.pdf"
```

#### Success Response (`201 Created`):
```json
{
  "resume_id": "res_8f7b2c1a4e90",
  "parsed_skills": [
    "AWS",
    "CI/CD",
    "Docker",
    "FastAPI",
    "Git",
    "Kubernetes",
    "Microservices",
    "PostgreSQL",
    "Python",
    "Redis",
    "REST API"
  ]
}
```

#### Error Responses:
* `400 Bad Request`: Empty file or unsupported format (e.g. `.docx`, `.exe`).
* `413 Request Entity Too Large`: File exceeds 10 MB.
* `422 Unprocessable Content`: Unreadable or corrupted binary data.

---

### 2.2 Calculate Heuristic ATS Score
* **Endpoint:** `GET /api/v1/resume/{resume_id}/ats-score?job_id={id}`
* **Parameters:**
  * `resume_id` *(path, string)*: ID of the previously uploaded resume.
  * `job_id` *(query, string)*: ID of the job posting to score against.

#### Request Example (cURL):
```bash
curl -X GET "http://localhost:8000/api/v1/resume/res_8f7b2c1a4e90/ats-score?job_id=job_py_01"
```

#### Success Response (`200 OK`):
```json
{
  "match_score": 88.5,
  "missing_keywords": [],
  "generated_by": "heuristic-v0"
}
```

#### Error Responses:
* `404 Not Found`: Resume ID or Job ID does not exist.

---

### 2.3 Get Personalized Job Recommendations
* **Endpoint:** `GET /api/v1/recommendations?user_id={id}&limit=50`
* **Parameters:**
  * `user_id` *(query or `X-User-ID` header, string)*: User ID.
  * `limit` *(optional, integer, default 50)*: Maximum number of results.

#### Request Example (cURL):
```bash
curl -X GET "http://localhost:8000/api/v1/recommendations?user_id=user_12345"
```

#### Success Response (`200 OK`):
```json
[
  {
    "job_id": "job_py_01",
    "match_percentage": 88.5,
    "generated_by": "heuristic-v0"
  },
  {
    "job_id": "job_fullstack_04",
    "match_percentage": 42.0,
    "generated_by": "heuristic-v0"
  }
]
```

#### Graceful Degradation:
* When a user has **not yet uploaded a resume**, the endpoint returns `[]` with status `200 OK`. This allows the frontend dashboard to display a friendly prompt without erroring.

---

## 3. Team Integration Guidelines

### 3.1 For Intern 1 (Team Lead & Gateway)
To mount this service directly inside the central API Gateway application:
```python
from backend.app.api.v1.router import api_v1_router

# In the Gateway main app:
app.include_router(api_v1_router, prefix="/api/v1")
```
When user authentication is verified in the Gateway, forward the user identifier via the `X-User-ID` header.

### 3.2 For Intern 4 (Frontend UI)
* **Resume Upload Flow:** Use standard `multipart/form-data` file input pointing to `/api/v1/resume/upload`.
* **Job Card ATS Compatibility:** When viewing a job card, fetch `/api/v1/resume/{resume_id}/ats-score?job_id={job_id}` to render the match percentage bar and missing skills chips.
* **Recommendations Feed:** Fetch `/api/v1/recommendations?user_id={currentUser.id}` on the dashboard. If the array is empty, render the "Upload Resume to Unlock Personalized Recommendations" widget.

### 3.3 For Intern 5 (QA & Platform)
* Run all automated tests: `pytest backend/tests/ -v`
* Automated tests cover:
  1. PDF and TXT file parsing
  2. Edge cases (empty files, unsupported formats, corrupted PDFs)
  3. Skill extraction accuracy and alias normalization
  4. Deterministic ATS scoring
  5. Recommendation ranking and user fallback logic
  6. OpenAPI specification schema adherence
