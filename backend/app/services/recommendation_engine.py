from backend.app.core.config import settings
from backend.app.models.schemas import JobRecommendationItem
from backend.app.services.ats_scorer import ATSScoringEngine, ats_scoring_engine
from backend.app.services.job_service_client import JobServiceClient, job_service_client
from backend.app.services.resume_parser import ResumeRepository, resume_repo


class RecommendationEngine:
    def __init__(
        self,
        resume_repository: ResumeRepository = resume_repo,
        job_client: JobServiceClient = job_service_client,
        scoring_engine: ATSScoringEngine = ats_scoring_engine,
    ):
        self.repo = resume_repository
        self.job_client = job_client
        self.scoring_engine = scoring_engine
        self.generated_by = settings.GENERATED_BY_TAG

    def get_recommendations_for_user(
        self, user_id: str | None = None, limit: int = 50
    ) -> list[JobRecommendationItem]:
        if not user_id:
            return []

        resume = self.repo.get_latest_by_user_id(user_id)
        if not resume:
            return []

        all_jobs = self.job_client.list_jobs()
        if not all_jobs:
            return []

        recommendations: list[JobRecommendationItem] = []

        for job in all_jobs:
            match_score, _ = self.scoring_engine.calculate_score(resume, job)
            recommendations.append(
                JobRecommendationItem(
                    job_id=job.job_id, match_percentage=match_score, generated_by=self.generated_by
                )
            )

        recommendations.sort(key=lambda item: (-item.match_percentage, item.job_id))

        return recommendations[:limit]


recommendation_engine = RecommendationEngine()
