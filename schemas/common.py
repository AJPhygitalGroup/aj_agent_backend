"""
Schemas comunes compartidos entre todos los agentes.
Usa Pydantic v2 para validación de datos.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Language(str, Enum):
    ES = "es"
    EN = "en"


class Platform(str, Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"


class ContentType(str, Enum):
    REEL = "reel"
    TIKTOK_VIDEO = "tiktok_video"
    CAROUSEL = "carousel"
    LINKEDIN_POST = "linkedin_post"
    YOUTUBE_VIDEO = "youtube_video"
    YOUTUBE_SHORT = "youtube_short"
    FACEBOOK_POST = "facebook_post"
    PODCAST_CLIP = "podcast_clip"


class PipelinePhase(str, Enum):
    IDLE = "idle"
    RESEARCHING = "researching"
    PLANNING = "planning"
    AWAITING_PLAN_APPROVAL = "awaiting_plan_approval"
    CREATING_CONTENT = "creating_content"
    PRODUCING_VISUALS = "producing_visuals"
    VALIDATING = "validating"
    AWAITING_CONTENT_APPROVAL = "awaiting_content_approval"
    SCHEDULING = "scheduling"
    AWAITING_SCHEDULE_APPROVAL = "awaiting_schedule_approval"
    PUBLISHED = "published"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    ERROR = "error"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class AgentOutput(BaseModel):
    """Base para todos los outputs de agentes."""
    agent_name: str
    timestamp: datetime = Field(default_factory=datetime.now)
    phase: PipelinePhase
    success: bool = True
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None


class ContentPiece(BaseModel):
    """Representa una pieza individual de contenido."""
    id: str
    title: str
    platform: Platform
    content_type: ContentType
    language: Language
    scheduled_date: Optional[datetime] = None
    scheduled_time: Optional[str] = None
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    tags: list[str] = Field(default_factory=list)
