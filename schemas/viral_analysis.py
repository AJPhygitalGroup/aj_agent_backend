"""Schema para el análisis viral del Viral Analyzer Agent."""

from pydantic import BaseModel, Field

from .common import AgentOutput, ContentType, Language, Platform


class VideoStructure(BaseModel):
    """Estructura analizada de un video viral."""
    hook_type: str = Field(description="Tipo de gancho: pregunta, estadística, controversia, etc.")
    hook_text: str = Field(description="Texto/concepto del hook")
    hook_duration_seconds: float | None = None
    body_structure: str = Field(description="Cómo se desarrolla el contenido")
    cta_type: str = Field(description="Tipo de CTA usado")
    total_duration_seconds: float | None = None


class ViralContentItem(BaseModel):
    """Un contenido viral analizado."""
    title: str
    platform: Platform
    content_type: ContentType
    url: str | None = None
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    tone: str = Field(description="educativo, entretenido, inspiracional, controvertido, etc.")
    music_type: str | None = Field(default=None, description="Tipo de música: trending audio, original, none")
    theme: str = Field(description="Tema principal del contenido")
    language: Language = Language.ES
    structure: VideoStructure | None = None
    why_viral: str = Field(description="Análisis de por qué se volvió viral")
    replicability_score: float = Field(ge=0, le=1, description="Qué tan fácil es replicar el formato")


class ViralPattern(BaseModel):
    """Patrón detectado entre varios contenidos virales."""
    pattern_name: str
    description: str
    frequency: int = Field(description="Cuántos contenidos usan este patrón")
    platforms: list[Platform] = Field(default_factory=list)
    example_hooks: list[str] = Field(default_factory=list)
    recommended_for: list[ContentType] = Field(default_factory=list)


class ViralAnalysisReport(AgentOutput):
    """Output completo del Viral Analyzer Agent."""
    agent_name: str = "viral_analyzer"
    analyzed_content: list[ViralContentItem] = Field(default_factory=list)
    detected_patterns: list[ViralPattern] = Field(default_factory=list)
    top_hooks: list[str] = Field(
        default_factory=list,
        description="Los hooks más efectivos encontrados"
    )
    trending_music: list[str] = Field(
        default_factory=list,
        description="Audios/música en tendencia"
    )
    format_recommendations: dict[str, str] = Field(
        default_factory=dict,
        description="Recomendaciones de formato por plataforma"
    )
