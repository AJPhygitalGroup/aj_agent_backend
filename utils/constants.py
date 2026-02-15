"""
Constantes globales del Content Engine.
"""

# Nombre del proyecto
PROJECT_NAME = "A&J Phygital Group Content Engine"
VERSION = "1.0.0"

# Agentes disponibles (en orden de ejecución)
AGENTS = [
    "orchestrator",
    "trend_researcher",
    "viral_analyzer",
    "content_planner",
    "copywriter",
    "seo_hashtag_specialist",
    "visual_designer",
    "carousel_creator",
    "avatar_video_producer",
    "brand_guardian",
    "scheduler",
    "engagement_analyst",
]

# Fases del pipeline con los agentes que ejecutan en cada fase
PIPELINE_PHASES = {
    "research": {
        "agents": ["trend_researcher", "viral_analyzer"],
        "parallel": True,
    },
    "planning": {
        "agents": ["content_planner"],
        "parallel": False,
        "checkpoint": True,
    },
    "content_creation": {
        "agents": ["copywriter", "seo_hashtag_specialist"],
        "parallel": True,
    },
    "visual_production": {
        "agents": ["visual_designer", "carousel_creator", "avatar_video_producer"],
        "parallel": True,
    },
    "validation": {
        "agents": ["brand_guardian"],
        "parallel": False,
        "checkpoint": True,
    },
    "publishing": {
        "agents": ["scheduler"],
        "parallel": False,
        "checkpoint": True,
    },
    "analysis": {
        "agents": ["engagement_analyst"],
        "parallel": False,
        "continuous": True,
    },
}

# Plataformas soportadas
PLATFORMS = ["instagram", "tiktok", "linkedin", "youtube", "facebook"]

# Tipos de contenido
CONTENT_TYPES = [
    "reel",
    "tiktok_video",
    "carousel",
    "linkedin_post",
    "youtube_video",
    "youtube_short",
    "facebook_post",
    "podcast_clip",
]
