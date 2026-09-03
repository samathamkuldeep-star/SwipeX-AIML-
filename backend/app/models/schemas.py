from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeUploadResponse(BaseModel):
    resume_id: str = Field(..., description="Unique identifier of the stored resume")
    parsed_skills: list[str] = Field(
        default_factory=list, description="List of normalized skills extracted from the resume"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "resume_id": "res_8f7b2c1a4e90",
                "parsed_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
            }
        }
    )


class ATSScoreResponse(BaseModel):
    match_score: float = Field(
        ..., ge=0, le=100, description="Heuristic ATS compatibility score between 0 and 100"
    )
    missing_keywords: list[str] = Field(
        default_factory=list, description="Job skills/keywords missing from the candidate's resume"
    )
    generated_by: str = Field(
        default="heuristic-v0", description="Model or engine identifier generating this score"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "match_score": 82.5,
                "missing_keywords": ["Kubernetes", "GraphQL"],
                "generated_by": "heuristic-v0",
            }
        }
    )


class JobRecommendationItem(BaseModel):
    job_id: str = Field(..., description="Unique identifier of the recommended job")
    match_percentage: float = Field(
        ..., ge=0, le=100, description="Overall heuristic match percentage for the candidate"
    )
    generated_by: str = Field(
        default="heuristic-v0", description="Engine version producing the recommendation"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "job_dev_101",
                "match_percentage": 88.0,
                "generated_by": "heuristic-v0",
            }
        }
    )


class ResumeRecord(BaseModel):
    resume_id: str
    user_id: str | None = None
    original_filename: str
    file_path: str
    file_type: str
    raw_text: str
    parsed_skills: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class JobDetail(BaseModel):
    job_id: str
    title: str
    company: str
    type: str = "Full-time"
    location: str = "Remote"
    remote: bool = True
    salary_range: str | None = "$90,000 - $130,000"
    skills: list[str] = Field(default_factory=list)
    description: str = ""
    posted_at: str | None = None


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None
