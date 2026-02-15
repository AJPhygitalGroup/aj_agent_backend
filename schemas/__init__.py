"""Schemas para comunicación entre agentes del Content Engine."""

from .brand_compliance import BrandComplianceReport, ComplianceCheck, ContentCompliance
from .common import (
    AgentOutput,
    ApprovalStatus,
    ContentPiece,
    ContentType,
    Language,
    PipelinePhase,
    Platform,
)
from .content_plan import ContentPlan, ContentSlot, DayPlan
from .content_scripts import CarouselScript, ContentScripts, PodcastScript, Script
from .engagement_report import (
    ContentInsight,
    EngagementReport,
    PlatformSummary,
    PostMetrics,
)
from .seo_optimizations import HashtagSet, SEOMetadata, SEOOptimizations
from .trend_report import PlatformTrends, TrendItem, TrendReport
from .viral_analysis import ViralAnalysisReport, ViralContentItem, ViralPattern

__all__ = [
    "AgentOutput",
    "ApprovalStatus",
    "BrandComplianceReport",
    "CarouselScript",
    "ComplianceCheck",
    "ContentCompliance",
    "ContentInsight",
    "ContentPiece",
    "ContentPlan",
    "ContentScripts",
    "ContentSlot",
    "ContentType",
    "DayPlan",
    "EngagementReport",
    "HashtagSet",
    "Language",
    "PipelinePhase",
    "Platform",
    "PlatformSummary",
    "PlatformTrends",
    "PodcastScript",
    "PostMetrics",
    "Script",
    "SEOMetadata",
    "SEOOptimizations",
    "TrendItem",
    "TrendReport",
    "ViralAnalysisReport",
    "ViralContentItem",
    "ViralPattern",
]
