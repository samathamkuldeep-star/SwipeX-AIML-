import re

from fastapi import HTTPException, status

from backend.app.core.config import settings
from backend.app.models.schemas import ATSScoreResponse, JobDetail, ResumeRecord
from backend.app.services.job_service_client import JobServiceClient, job_service_client
from backend.app.services.resume_parser import ResumeRepository, resume_repo
from backend.app.services.skill_extractor import skill_extractor


class ATSScoringEngine:
    def __init__(
        self,
        resume_repository: ResumeRepository = resume_repo,
        job_client: JobServiceClient = job_service_client,
        skills_weight: float = settings.REQUIRED_SKILLS_WEIGHT,
        keyword_weight: float = settings.KEYWORD_OVERLAP_WEIGHT,
    ):
        self.repo = resume_repository
        self.job_client = job_client
        self.skills_weight = skills_weight
        self.keyword_weight = keyword_weight
        self.generated_by = settings.GENERATED_BY_TAG

    def _extract_job_keywords(self, job: JobDetail) -> set[str]:
        stopwords = {
            "a",
            "an",
            "the",
            "and",
            "or",
            "in",
            "on",
            "at",
            "to",
            "for",
            "with",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "will",
            "we",
            "you",
            "our",
            "looking",
            "seeking",
            "experienced",
            "join",
            "team",
            "responsibilities",
            "experience",
            "years",
            "work",
            "candidate",
            "role",
            "position",
        }
        text = f"{job.title} {job.description}".lower()
        words = re.findall(r"\b[a-z0-9+#.-]{2,}\b", text)
        keywords = {w for w in words if w not in stopwords and len(w) > 2}
        return keywords

    def calculate_score(self, resume: ResumeRecord, job: JobDetail) -> tuple[float, list[str]]:
        resume_skills_set = set(resume.parsed_skills)

        job_skills_normalized = skill_extractor.normalize_skills(job.skills)
        job_skills_set = set(job_skills_normalized)

        if job_skills_set:
            matched_skills = resume_skills_set.intersection(job_skills_set)
            skill_ratio = len(matched_skills) / len(job_skills_set)
            missing_skills = sorted(job_skills_set - resume_skills_set)
        else:
            skill_ratio = 1.0
            missing_skills = []

        job_keywords = self._extract_job_keywords(job)
        resume_text_lower = resume.raw_text.lower()

        if job_keywords:
            matched_keywords = {
                kw
                for kw in job_keywords
                if re.search(r"\b" + re.escape(kw) + r"\b", resume_text_lower)
            }
            keyword_ratio = len(matched_keywords) / len(job_keywords)
        else:
            keyword_ratio = 1.0

        raw_score = (skill_ratio * self.skills_weight) + (keyword_ratio * self.keyword_weight)
        final_score = round(min(max(raw_score * 100.0, 0.0), 100.0), 1)

        return final_score, missing_skills

    def get_ats_score(self, resume_id: str, job_id: str) -> ATSScoreResponse:
        resume = self.repo.get_by_id(resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID '{resume_id}' not found.",
            )

        job = self.job_client.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID '{job_id}' not found.",
            )

        match_score, missing_keywords = self.calculate_score(resume, job)

        return ATSScoreResponse(
            match_score=match_score,
            missing_keywords=missing_keywords,
            generated_by=self.generated_by,
        )


ats_scoring_engine = ATSScoringEngine()
