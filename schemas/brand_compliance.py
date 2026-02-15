"""Schema para el reporte de compliance del Brand Guardian Agent."""

from pydantic import BaseModel, Field

from .common import AgentOutput, ApprovalStatus


class ComplianceCheck(BaseModel):
    """Resultado de un check individual de compliance."""
    check_type: str = Field(description="tone_of_voice, color_palette, typography, etc.")
    passed: bool
    score: float = Field(ge=0, le=1)
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class ContentCompliance(BaseModel):
    """Compliance de una pieza individual de contenido."""
    content_slot_id: str
    checks: list[ComplianceCheck] = Field(default_factory=list)
    overall_score: float = Field(ge=0, le=1)
    approved: bool = False
    critical_issues: list[str] = Field(default_factory=list)
    minor_issues: list[str] = Field(default_factory=list)
    recommendation: ApprovalStatus = ApprovalStatus.PENDING


class BrandComplianceReport(AgentOutput):
    """Output completo del Brand Guardian Agent."""
    agent_name: str = "brand_guardian"
    content_reviews: list[ContentCompliance] = Field(default_factory=list)
    overall_batch_score: float = Field(ge=0, le=1, default=0.0)
    total_reviewed: int = 0
    total_approved: int = 0
    total_needs_revision: int = 0
    total_rejected: int = 0
    common_issues: list[str] = Field(default_factory=list)
    batch_recommendation: ApprovalStatus = ApprovalStatus.PENDING
