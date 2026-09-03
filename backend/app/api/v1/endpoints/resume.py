from fastapi import APIRouter, Depends, File, Form, Header, Query, UploadFile, status

from backend.app.models.schemas import (
    ATSScoreResponse,
    ResumeUploadResponse,
)
from backend.app.services.ats_scorer import ATSScoringEngine, ats_scoring_engine
from backend.app.services.resume_parser import (
    ResumeParserService,
    resume_parser_service,
)

router = APIRouter(prefix="/resume", tags=["Resume & Career Intelligence"])


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a candidate resume",
    description="Accepts a PDF or TXT resume file via multipart/form-data, securely stores it, extracts technical skills, and returns the assigned resume_id and parsed_skills list.",
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file (.pdf or .txt)"),
    user_id: str | None = Form(None, description="Optional user ID to associate with this resume"),
    x_user_id: str | None = Header(
        None, alias="X-User-ID", description="Optional user ID from Auth Gateway header"
    ),
    parser: ResumeParserService = Depends(lambda: resume_parser_service),
) -> ResumeUploadResponse:
    resolved_user_id = user_id or x_user_id
    response = await parser.parse_and_store_upload(upload_file=file, user_id=resolved_user_id)
    return response


@router.get(
    "/{resume_id}/ats-score",
    response_model=ATSScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate heuristic ATS match score against a job",
    description="Computes rule-based ATS compatibility score ('heuristic-v0') between the parsed resume and specified job, listing missing keywords.",
)
def get_resume_ats_score(
    resume_id: str,
    job_id: str = Query(..., description="ID of the job to score against"),
    scorer: ATSScoringEngine = Depends(lambda: ats_scoring_engine),
) -> ATSScoreResponse:
    return scorer.get_ats_score(resume_id=resume_id, job_id=job_id)
