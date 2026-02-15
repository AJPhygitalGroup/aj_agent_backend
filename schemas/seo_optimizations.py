"""Schema para las optimizaciones SEO del SEO & Hashtag Specialist Agent."""

from pydantic import BaseModel, Field

from .common import AgentOutput, Platform


class HashtagSet(BaseModel):
    """Set de hashtags optimizado para una pieza de contenido."""
    content_slot_id: str
    platform: Platform
    primary_hashtags: list[str] = Field(
        default_factory=list,
        description="Hashtags principales de alto volumen"
    )
    secondary_hashtags: list[str] = Field(
        default_factory=list,
        description="Hashtags de nicho medio"
    )
    long_tail_hashtags: list[str] = Field(
        default_factory=list,
        description="Hashtags específicos de cola larga"
    )
    branded_hashtags: list[str] = Field(default_factory=list)
    total_hashtags: int = 0


class SEOMetadata(BaseModel):
    """Metadatos SEO para una pieza de contenido."""
    content_slot_id: str
    platform: Platform
    optimized_title: str
    optimized_description: str
    keywords: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    alt_text_suggestions: list[str] = Field(
        default_factory=list,
        description="Alt text para imágenes"
    )


class SEOOptimizations(AgentOutput):
    """Output completo del SEO & Hashtag Specialist Agent."""
    agent_name: str = "seo_hashtag_specialist"
    hashtag_sets: list[HashtagSet] = Field(default_factory=list)
    seo_metadata: list[SEOMetadata] = Field(default_factory=list)
    trending_hashtags_global: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Hashtags trending por plataforma"
    )
    keyword_opportunities: list[str] = Field(
        default_factory=list,
        description="Keywords con buen volumen y baja competencia"
    )
