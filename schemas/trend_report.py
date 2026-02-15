"""Schema para el reporte de tendencias del Trend Researcher Agent."""

from pydantic import BaseModel, Field

from .common import AgentOutput, Language, Platform


class TrendItem(BaseModel):
    """Una tendencia individual detectada."""
    topic: str
    description: str
    platform: Platform
    relevance_score: float = Field(ge=0, le=1, description="0-1, relevancia al nicho")
    engagement_level: str = Field(description="low, medium, high, viral")
    source_url: str | None = None
    hashtags: list[str] = Field(default_factory=list)
    language: Language = Language.ES
    keyword_volume: int | None = None
    rising: bool = True  # Si la tendencia está en alza


class PlatformTrends(BaseModel):
    """Tendencias agrupadas por plataforma."""
    platform: Platform
    trends: list[TrendItem] = Field(default_factory=list)
    scraped_at: str | None = None


class TrendReport(AgentOutput):
    """Output completo del Trend Researcher Agent."""
    agent_name: str = "trend_researcher"
    platform_trends: list[PlatformTrends] = Field(default_factory=list)
    top_global_trends: list[TrendItem] = Field(
        default_factory=list,
        description="Top tendencias combinadas de todas las plataformas"
    )
    recommended_topics: list[str] = Field(
        default_factory=list,
        description="Temas recomendados basados en tendencias + nicho"
    )
    nicho_relevance_summary: str = ""
