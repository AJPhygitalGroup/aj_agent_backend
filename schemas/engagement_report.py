"""Schema para el reporte de engagement del Engagement Analyst Agent."""

from datetime import datetime

from pydantic import BaseModel, Field

from .common import AgentOutput, ContentType, Platform


class PostMetrics(BaseModel):
    """Métricas de una publicación individual."""
    post_id: str
    platform: Platform
    content_type: ContentType
    published_at: datetime | None = None
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    reach: int = 0
    impressions: int = 0
    engagement_rate: float = 0.0
    watch_time_seconds: float | None = None
    click_through_rate: float | None = None
    follower_growth: int = 0


class PlatformSummary(BaseModel):
    """Resumen de métricas por plataforma."""
    platform: Platform
    total_posts: int = 0
    avg_engagement_rate: float = 0.0
    total_reach: int = 0
    total_impressions: int = 0
    best_performing_post_id: str | None = None
    worst_performing_post_id: str | None = None
    follower_count: int | None = None
    follower_growth: int = 0


class ContentInsight(BaseModel):
    """Insight derivado del análisis de engagement."""
    insight: str
    action_recommendation: str
    confidence: float = Field(ge=0, le=1)
    related_platforms: list[Platform] = Field(default_factory=list)


class EngagementReport(AgentOutput):
    """Output completo del Engagement Analyst Agent."""
    agent_name: str = "engagement_analyst"
    reporting_period_start: datetime | None = None
    reporting_period_end: datetime | None = None
    post_metrics: list[PostMetrics] = Field(default_factory=list)
    platform_summaries: list[PlatformSummary] = Field(default_factory=list)
    top_performers: list[PostMetrics] = Field(
        default_factory=list,
        description="Top 5 publicaciones por engagement"
    )
    insights: list[ContentInsight] = Field(default_factory=list)
    recommendations_for_next_cycle: list[str] = Field(default_factory=list)
