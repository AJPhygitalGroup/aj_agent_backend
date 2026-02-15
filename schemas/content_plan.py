"""Schema para el plan de contenido del Content Planner Agent."""

from datetime import date

from pydantic import BaseModel, Field

from .common import (
    AgentOutput,
    ApprovalStatus,
    ContentType,
    Language,
    Platform,
)


class ContentSlot(BaseModel):
    """Un slot individual en el calendario de contenido."""
    id: str
    date: date
    time: str = Field(description="Hora de publicación HH:MM")
    platform: Platform
    content_type: ContentType
    language: Language
    topic: str
    angle: str = Field(description="Ángulo/enfoque específico del tema")
    content_pillar: str = Field(description="Pilar de contenido al que pertenece")
    hook_idea: str = Field(description="Idea para el gancho/hook")
    reference_trend: str | None = Field(
        default=None,
        description="Tendencia de referencia que inspira esta pieza"
    )
    viral_pattern: str | None = Field(
        default=None,
        description="Patrón viral sugerido para esta pieza"
    )
    priority: str = Field(default="medium", description="low, medium, high")
    notes: str = ""
    approval_status: ApprovalStatus = ApprovalStatus.PENDING


class DayPlan(BaseModel):
    """Plan de un día completo."""
    date: date
    slots: list[ContentSlot] = Field(default_factory=list)
    total_posts: int = 0


class ContentPlan(AgentOutput):
    """Output completo del Content Planner Agent."""
    agent_name: str = "content_planner"
    week_start: date
    week_end: date
    days: list[DayPlan] = Field(default_factory=list)
    total_pieces: int = 0
    platform_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Cantidad de piezas por plataforma"
    )
    content_type_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Cantidad de piezas por tipo de contenido"
    )
    pillar_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Cantidad de piezas por pilar de contenido"
    )
    google_sheet_url: str | None = None
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
