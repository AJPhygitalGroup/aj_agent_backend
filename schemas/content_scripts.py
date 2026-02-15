"""Schema para los guiones del Copywriter Agent."""

from pydantic import BaseModel, Field

from .common import AgentOutput, ContentType, Language, Platform


class Script(BaseModel):
    """Un guión individual para una pieza de contenido."""
    content_slot_id: str = Field(description="ID del ContentSlot al que corresponde")
    platform: Platform
    content_type: ContentType
    language: Language
    title: str
    hook: str = Field(description="Texto del gancho/hook (primeros segundos)")
    body: str = Field(description="Cuerpo del guión/contenido")
    cta: str = Field(description="Call to action")
    full_script: str = Field(description="Guión completo formateado")
    caption: str = Field(description="Descripción/caption para la publicación")
    word_count: int = 0
    estimated_duration_seconds: int | None = None
    notes_for_visual: str = Field(
        default="",
        description="Indicaciones para el Visual Designer"
    )
    notes_for_avatar: str = Field(
        default="",
        description="Indicaciones para el Avatar Video Producer"
    )


class CarouselScript(BaseModel):
    """Guión específico para carruseles."""
    content_slot_id: str
    platform: Platform
    language: Language
    title: str
    slides: list[dict] = Field(
        default_factory=list,
        description="Lista de slides con {slide_number, headline, body, visual_notes}"
    )
    caption: str
    total_slides: int = 0


class PodcastScript(BaseModel):
    """Guión específico para podcasts."""
    content_slot_id: str
    language: Language
    title: str
    intro: str
    segments: list[dict] = Field(
        default_factory=list,
        description="Lista de segmentos con {segment_name, content, duration_minutes}"
    )
    outro: str
    total_duration_minutes: int = 0
    key_takeaways: list[str] = Field(default_factory=list)


class ContentScripts(AgentOutput):
    """Output completo del Copywriter Agent."""
    agent_name: str = "copywriter"
    scripts: list[Script] = Field(default_factory=list)
    carousel_scripts: list[CarouselScript] = Field(default_factory=list)
    podcast_scripts: list[PodcastScript] = Field(default_factory=list)
    total_pieces: int = 0
