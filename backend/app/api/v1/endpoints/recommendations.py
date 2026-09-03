from fastapi import APIRouter, Depends, Header, Query, status

from backend.app.models.schemas import JobRecommendationItem
from backend.app.services.recommendation_engine import (
    RecommendationEngine,
    recommendation_engine,
)

router = APIRouter(tags=["Recommendations & Career Intelligence"])


@router.get(
    "/recommendations",
    response_model=list[JobRecommendationItem],
    status_code=status.HTTP_200_OK,
    summary="Get heuristic job recommendations for a user",
    description="Returns a ranked list of job recommendations based on skill and keyword overlap between the user's latest uploaded resume and available jobs.",
)
def get_recommendations(
    user_id: str | None = Query(None, description="User ID to retrieve recommendations for"),
    x_user_id: str | None = Header(
        None, alias="X-User-ID", description="Optional user ID from Auth Gateway header"
    ),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of recommendations to return"),
    engine: RecommendationEngine = Depends(lambda: recommendation_engine),
) -> list[JobRecommendationItem]:
    resolved_user_id = user_id or x_user_id
    return engine.get_recommendations_for_user(user_id=resolved_user_id, limit=limit)
