"""
A&J Phygital Group - Content Engine API
FastAPI backend que expone los agentes como endpoints REST.
Se despliega en el VPS con Docker/Easypanel.
"""

import json
import logging
import os
import sys
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env BEFORE anything else
load_dotenv(Path(__file__).parent / ".env", override=True)

from utils.helpers import get_project_root, load_json, save_json

# Configure logging for the API
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("content-engine-api")

app = FastAPI(
    title="A&J Content Engine API",
    version="1.0.0",
    description="Backend API for the AI Content Generation Pipeline",
)

# CORS - allow Vercel dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        os.getenv("DASHBOARD_URL", ""),
        # Vercel domains
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"https://.*\.vercel\.app",
)

PROJECT_ROOT = get_project_root()
OUTPUTS_DIR = PROJECT_ROOT / "data" / "outputs"
INPUTS_DIR = PROJECT_ROOT / "data" / "inputs"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "inputs" / "templates"
BRAND_ASSETS_DIR = PROJECT_ROOT / "data" / "brand_assets"
FONTS_DIR = BRAND_ASSETS_DIR / "fonts"


# ── Image / file serving ──────────────────────────────
# Mount the outputs directory so the dashboard can load
# generated images, carousel slides, etc.

@app.get("/api/images/{filename:path}")
def serve_image(filename: str):
    """Serve a generated image from data/outputs/images/."""
    file_path = OUTPUTS_DIR / "images" / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    media = "image/png" if filename.endswith(".png") else "image/jpeg"
    return FileResponse(file_path, media_type=media)


@app.get("/api/carousels/slides/{filename:path}")
def serve_carousel_slide(filename: str):
    """Serve a generated carousel slide from data/outputs/carousels/."""
    file_path = OUTPUTS_DIR / "carousels" / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Carousel slide not found")
    media = "image/png" if filename.endswith(".png") else "image/jpeg"
    return FileResponse(file_path, media_type=media)


# Track running pipeline
_pipeline_lock = threading.Lock()
_pipeline_running = False

# Track running individual agents
_agent_lock = threading.Lock()
_running_agents: dict[str, dict] = {}  # {agent_name: {status, started_at, error?}}

# Global agent registry (used by both pipeline and individual runs)
AGENT_REGISTRY = {
    "trend_researcher": ("agents.trend_researcher.agent", "TrendResearcherAgent"),
    "viral_analyzer": ("agents.viral_analyzer.agent", "ViralAnalyzerAgent"),
    "content_planner": ("agents.content_planner.agent", "ContentPlannerAgent"),
    "copywriter": ("agents.copywriter.agent", "CopywriterAgent"),
    "seo_hashtag_specialist": ("agents.seo_hashtag_specialist.agent", "SEOHashtagSpecialistAgent"),
    "visual_designer": ("agents.visual_designer.agent", "VisualDesignerAgent"),
    "carousel_creator": ("agents.carousel_creator.agent", "CarouselCreatorAgent"),
    "avatar_video_producer": ("agents.avatar_video_producer.agent", "AvatarVideoProducerAgent"),
    "brand_guardian": ("agents.brand_guardian.agent", "BrandGuardianAgent"),
    "scheduler": ("agents.scheduler.agent", "SchedulerAgent"),
    "engagement_analyst": ("agents.engagement_analyst.agent", "EngagementAnalystAgent"),
}

# Human-readable agent info for the dashboard
AGENT_INFO = {
    "trend_researcher": {"label": "Trend Researcher", "description": "Investiga tendencias en redes sociales y Google", "phase": 1, "icon": "search"},
    "viral_analyzer": {"label": "Viral Analyzer", "description": "Analiza contenido viral y extrae patrones", "phase": 1, "icon": "trending"},
    "content_planner": {"label": "Content Planner", "description": "Genera el plan de contenido semanal", "phase": 2, "icon": "calendar"},
    "copywriter": {"label": "Copywriter", "description": "Escribe guiones, captions y CTAs", "phase": 3, "icon": "edit"},
    "seo_hashtag_specialist": {"label": "SEO & Hashtags", "description": "Optimiza SEO, hashtags y keywords", "phase": 3, "icon": "hash"},
    "visual_designer": {"label": "Visual Designer", "description": "Genera imagenes para hooks y thumbnails", "phase": 4, "icon": "image"},
    "carousel_creator": {"label": "Carousel Creator", "description": "Crea carruseles para IG y LinkedIn", "phase": 4, "icon": "layers"},
    "avatar_video_producer": {"label": "Avatar Video", "description": "Genera videos con avatar IA (HeyGen)", "phase": 4, "icon": "video"},
    "brand_guardian": {"label": "Brand Guardian", "description": "Valida que el contenido cumpla con la marca", "phase": 5, "icon": "shield"},
    "scheduler": {"label": "Scheduler", "description": "Programa publicaciones en redes sociales", "phase": 6, "icon": "clock"},
    "engagement_analyst": {"label": "Engagement Analyst", "description": "Analiza metricas post-publicacion", "phase": 7, "icon": "chart"},
}


# ── Models ──────────────────────────────────────────────

class CampaignRequest(BaseModel):
    brief: str
    platforms: list[str] = ["instagram", "tiktok", "linkedin", "youtube", "facebook"]
    language: list[str] = ["es", "en"]


class AgentRunRequest(BaseModel):
    agent_name: str
    custom_prompt: str = ""  # optional: override the agent's default prompt


class ApprovalRequest(BaseModel):
    checkpoint: str
    item_id: str
    decision: str = ""  # approved, rejected, revision
    status: str = ""  # alias — frontend sends 'status' instead of 'decision'
    feedback: str = ""


# ── Helpers ─────────────────────────────────────────────

def get_latest_file(prefix: str) -> dict | None:
    """Get the latest output file for an agent."""
    files = sorted(
        OUTPUTS_DIR.glob(f"{prefix}_*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    if files:
        return load_json(files[0])
    return None


def get_pipeline_state() -> dict:
    state_path = OUTPUTS_DIR / "pipeline_state.json"
    if state_path.exists():
        return load_json(state_path)
    return {"status": "idle", "phase": 0}


def get_campaign_brief() -> dict | None:
    brief_path = INPUTS_DIR / "campaign_brief.json"
    if brief_path.exists():
        return load_json(brief_path)
    return None


# ── Pipeline Runner (background thread) ────────────────

def _run_pipeline_thread(brief: str, platforms: list[str], language: list[str]):
    """Runs the full pipeline in a background thread."""
    global _pipeline_running
    import importlib
    import time

    logger.info("Pipeline thread started for brief: %s", brief[:100])

    # Verify critical env vars upfront
    missing_keys = []
    for key in ["ANTHROPIC_API_KEY"]:
        if not os.getenv(key):
            missing_keys.append(key)
    if missing_keys:
        logger.error("Missing critical env vars: %s", missing_keys)
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        save_json({
            "status": "error",
            "error": f"Missing environment variables: {', '.join(missing_keys)}. Configure them in Easypanel.",
            "campaign_brief": brief,
        }, OUTPUTS_DIR / "pipeline_state.json")
        with _pipeline_lock:
            _pipeline_running = False
        return

    try:
        from agents.orchestrator.agent import PHASES
    except Exception as e:
        logger.error("Failed to import PHASES: %s\n%s", e, traceback.format_exc())
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        save_json({
            "status": "error",
            "error": f"Import error: {e}",
            "traceback": traceback.format_exc(),
            "campaign_brief": brief,
        }, OUTPUTS_DIR / "pipeline_state.json")
        with _pipeline_lock:
            _pipeline_running = False
        return

    try:
        # Save campaign brief
        INPUTS_DIR.mkdir(parents=True, exist_ok=True)
        campaign_data = {
            "brief": brief,
            "platforms": platforms,
            "language": language,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "running",
        }
        save_json(campaign_data, INPUTS_DIR / "campaign_brief.json")

        # Update pipeline state
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        save_json({
            "status": "running",
            "phase": 0,
            "campaign_brief": brief,
            "started_at": campaign_data["timestamp"],
        }, OUTPUTS_DIR / "pipeline_state.json")

        logger.info("Pipeline state saved, starting phases...")

        # Run phases
        for phase_num in sorted(PHASES.keys()):
            phase_info = PHASES[phase_num]
            logger.info("=== PHASE %d: %s ===", phase_num, phase_info["name"])

            # Update state
            save_json({
                "status": "running",
                "phase": phase_num,
                "phase_name": phase_info["name"],
                "campaign_brief": brief,
                "started_at": campaign_data["timestamp"],
            }, OUTPUTS_DIR / "pipeline_state.json")

            # Run agents in phase
            for agent_name in phase_info["agents"]:
                if agent_name not in AGENT_REGISTRY:
                    logger.warning("Agent %s not in registry, skipping", agent_name)
                    continue
                module_path, class_name = AGENT_REGISTRY[agent_name]
                logger.info("Running agent: %s (%s.%s)", agent_name, module_path, class_name)
                try:
                    module = importlib.import_module(module_path)
                    agent_class = getattr(module, class_name)
                    agent_instance = agent_class()
                    result = agent_instance.run()
                    logger.info("Agent %s completed. Result length: %d", agent_name, len(result) if result else 0)
                except Exception as e:
                    logger.error("Agent %s failed: %s\n%s", agent_name, e, traceback.format_exc())
                    # Save error to state but continue pipeline
                    save_json({
                        "status": "running",
                        "phase": phase_num,
                        "phase_name": phase_info["name"],
                        "campaign_brief": brief,
                        "started_at": campaign_data["timestamp"],
                        "last_error": f"Agent {agent_name}: {e}",
                    }, OUTPUTS_DIR / "pipeline_state.json")

            # Checkpoints - pause and wait for approval via API
            if phase_info.get("checkpoint"):
                logger.info("CHECKPOINT at phase %d - waiting for approval", phase_num)
                save_json({
                    "status": "waiting_approval",
                    "phase": phase_num,
                    "phase_name": phase_info["name"],
                    "checkpoint": True,
                    "campaign_brief": brief,
                    "started_at": campaign_data["timestamp"],
                }, OUTPUTS_DIR / "pipeline_state.json")

                # Wait for approval (poll every 5 seconds)
                while True:
                    state = get_pipeline_state()
                    if state.get("status") == "approved":
                        logger.info("Checkpoint approved, continuing...")
                        save_json({
                            "status": "running",
                            "phase": phase_num,
                            "phase_name": phase_info["name"],
                            "campaign_brief": brief,
                            "started_at": campaign_data["timestamp"],
                        }, OUTPUTS_DIR / "pipeline_state.json")
                        break
                    elif state.get("status") == "stopped_by_user":
                        logger.info("Pipeline stopped by user at phase %d", phase_num)
                        campaign_data["status"] = "stopped"
                        save_json(campaign_data, INPUTS_DIR / "campaign_brief.json")
                        return
                    time.sleep(5)

        # Completed
        logger.info("Pipeline completed successfully!")
        campaign_data["status"] = "completed"
        save_json(campaign_data, INPUTS_DIR / "campaign_brief.json")
        save_json({
            "status": "completed",
            "phase": 7,
            "campaign_brief": brief,
            "started_at": campaign_data["timestamp"],
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }, OUTPUTS_DIR / "pipeline_state.json")

    except Exception as e:
        logger.error("Pipeline fatal error: %s\n%s", e, traceback.format_exc())
        try:
            save_json({
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "campaign_brief": brief,
            }, OUTPUTS_DIR / "pipeline_state.json")
        except Exception as save_err:
            logger.error("Could not save error state: %s", save_err)
    finally:
        with _pipeline_lock:
            _pipeline_running = False
        logger.info("Pipeline thread finished, _pipeline_running set to False")


# ── Endpoints ───────────────────────────────────────────

@app.get("/")
def root():
    return {"service": "A&J Content Engine API", "status": "ok"}


@app.get("/api/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


# -- Campaigns --

@app.get("/api/campaigns")
def get_campaign_status():
    """Get current campaign and pipeline status."""
    return {
        "pipeline": get_pipeline_state(),
        "campaign": get_campaign_brief(),
    }


@app.post("/api/campaigns")
def start_campaign(req: CampaignRequest):
    """Start a new campaign with a brief."""
    global _pipeline_running

    if len(req.brief.strip()) < 3:
        raise HTTPException(400, "Brief must be at least 3 characters")

    with _pipeline_lock:
        if _pipeline_running:
            # Check if the pipeline is actually stuck (error state but flag still True)
            state = get_pipeline_state()
            if state.get("status") in ("error", "idle", "completed", "stopped_by_user"):
                logger.warning("Pipeline flag was stuck (state=%s), auto-resetting", state.get("status"))
                _pipeline_running = False
            else:
                raise HTTPException(409, "A campaign is already running. Use POST /api/pipeline/reset to force-reset.")
        _pipeline_running = True

    logger.info("Starting campaign: %s", req.brief.strip()[:100])

    # Launch pipeline in background thread
    thread = threading.Thread(
        target=_run_pipeline_thread,
        args=(req.brief.strip(), req.platforms, req.language),
        daemon=True,
    )
    thread.start()

    return {"status": "started", "brief": req.brief.strip()}


# -- Pipeline Control --

@app.post("/api/pipeline/approve")
def approve_checkpoint():
    """Approve a checkpoint to continue the pipeline."""
    state = get_pipeline_state()
    if state.get("status") != "waiting_approval":
        raise HTTPException(400, "No checkpoint waiting for approval")

    state["status"] = "approved"
    save_json(state, OUTPUTS_DIR / "pipeline_state.json")
    return {"status": "approved", "phase": state.get("phase")}


@app.post("/api/pipeline/stop")
def stop_pipeline():
    """Stop the running pipeline."""
    state = get_pipeline_state()
    state["status"] = "stopped_by_user"
    save_json(state, OUTPUTS_DIR / "pipeline_state.json")
    return {"status": "stopped"}


@app.get("/api/pipeline")
def get_pipeline():
    """Get pipeline state with trend summary."""
    pipeline = get_pipeline_state()
    trends = get_latest_file("trend_researcher")

    trend_summary = None
    if trends:
        trend_summary = {
            "date": trends.get("generation_date", ""),
            "top_trends": trends.get("top_global_trends", [])[:5],
            "recommended_topics": trends.get("recommended_topics", [])[:5],
            "platforms_covered": [
                pt.get("platform", "") for pt in trends.get("platform_trends", [])
            ],
        }

    return {"pipeline": pipeline, "trends": trend_summary}


# -- Individual Agent Execution --

@app.get("/api/agents")
def list_agents():
    """List all available agents with their info and running status."""
    agents = []
    for name, info in AGENT_INFO.items():
        with _agent_lock:
            run_status = _running_agents.get(name)
        agents.append({
            "name": name,
            "label": info["label"],
            "description": info["description"],
            "phase": info["phase"],
            "icon": info["icon"],
            "is_running": run_status is not None and run_status.get("status") == "running",
            "last_run": run_status,
        })
    return {"agents": agents}


@app.post("/api/agents/run")
def run_single_agent(req: AgentRunRequest):
    """Run a single agent independently (not as part of the pipeline)."""
    import importlib

    agent_name = req.agent_name
    if agent_name not in AGENT_REGISTRY:
        raise HTTPException(400, f"Unknown agent: {agent_name}. Available: {', '.join(AGENT_REGISTRY.keys())}")

    # Check if already running
    with _agent_lock:
        existing = _running_agents.get(agent_name)
        if existing and existing.get("status") == "running":
            raise HTTPException(409, f"Agent {agent_name} is already running")

    # Check env
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(400, "ANTHROPIC_API_KEY not configured")

    # Mark as running
    with _agent_lock:
        _running_agents[agent_name] = {
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "custom_prompt": bool(req.custom_prompt),
        }

    def _run_agent():
        try:
            module_path, class_name = AGENT_REGISTRY[agent_name]
            module = importlib.import_module(module_path)
            agent_class = getattr(module, class_name)
            agent_instance = agent_class()

            logger.info("Running individual agent: %s (custom_prompt=%s)", agent_name, bool(req.custom_prompt))

            if req.custom_prompt:
                result = agent_instance.run(custom_prompt=req.custom_prompt)
            else:
                result = agent_instance.run()

            logger.info("Agent %s completed. Result length: %d", agent_name, len(result) if result else 0)

            with _agent_lock:
                _running_agents[agent_name] = {
                    "status": "completed",
                    "started_at": _running_agents[agent_name]["started_at"],
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "result_length": len(result) if result else 0,
                }

        except Exception as e:
            logger.error("Agent %s failed: %s\n%s", agent_name, e, traceback.format_exc())
            with _agent_lock:
                _running_agents[agent_name] = {
                    "status": "error",
                    "started_at": _running_agents.get(agent_name, {}).get("started_at", ""),
                    "error": str(e),
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }

    thread = threading.Thread(target=_run_agent, daemon=True)
    thread.start()

    return {
        "status": "started",
        "agent": agent_name,
        "label": AGENT_INFO.get(agent_name, {}).get("label", agent_name),
        "message": f"Agent {agent_name} is now running in the background.",
    }


@app.get("/api/agents/status")
def get_agents_status():
    """Get the status of all agents (running, completed, error)."""
    with _agent_lock:
        return {"agents": dict(_running_agents)}


@app.get("/api/agents/status/{agent_name}")
def get_agent_status(agent_name: str):
    """Get the status of a specific agent."""
    with _agent_lock:
        status = _running_agents.get(agent_name)
    if not status:
        return {"agent": agent_name, "status": "idle"}
    return {"agent": agent_name, **status}


# -- Content --

@app.get("/api/content/{content_type}")
def get_content(content_type: str):
    """Get content by type: plan, scripts, compliance, trends, schedule."""
    type_map = {
        "plan": "content_planner",
        "scripts": "copywriter",
        "compliance": "brand_guardian",
        "trends": "trend_researcher",
        "viral": "viral_analyzer",
        "schedule": "scheduler",
        "seo": "seo_hashtag_specialist",
        "images": "visual_designer",
        "carousels": "carousel_creator",
        "engagement": "engagement_analyst",
    }

    if content_type not in type_map:
        raise HTTPException(400, f"Invalid type. Use: {', '.join(type_map.keys())}")

    data = get_latest_file(type_map[content_type])
    if not data:
        return {"data": None, "message": f"No {content_type} data found"}

    # Inject image URLs so the dashboard can display them
    if content_type == "images" and isinstance(data, dict):
        for img in data.get("images_generated", []):
            if "filename" in img:
                img["url"] = f"/api/images/{img['filename']}"
    elif content_type == "carousels" and isinstance(data, dict):
        for carousel in data.get("carousels", []):
            for slide in carousel.get("slides", []):
                if "filename" in slide:
                    slide["url"] = f"/api/carousels/slides/{slide['filename']}"

    return {"data": data}


# -- Approvals --

@app.get("/api/approvals")
def get_approvals():
    """Get all approval decisions."""
    approvals_path = OUTPUTS_DIR / "approvals.json"
    if approvals_path.exists():
        return load_json(approvals_path)
    return {"decisions": []}


@app.post("/api/approvals")
def save_approval(req: ApprovalRequest):
    """Save an approval decision."""
    approvals_path = OUTPUTS_DIR / "approvals.json"
    data = load_json(approvals_path) if approvals_path.exists() else {"decisions": []}

    # Frontend sends 'status', backend model has 'decision' — accept either
    resolved_decision = req.decision or req.status or "approved"
    data["decisions"].append({
        "checkpoint": req.checkpoint,
        "item_id": req.item_id,
        "decision": resolved_decision,
        "status": resolved_decision,
        "feedback": req.feedback,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    save_json(data, approvals_path)
    return {"status": "saved", "total_decisions": len(data["decisions"])}


# -- Debug & Maintenance --

@app.post("/api/pipeline/reset")
def reset_pipeline():
    """Force-reset the pipeline state (clears stuck flag)."""
    global _pipeline_running
    with _pipeline_lock:
        was_running = _pipeline_running
        _pipeline_running = False
    save_json({"status": "idle", "phase": 0}, OUTPUTS_DIR / "pipeline_state.json")
    logger.info("Pipeline reset. Was running: %s", was_running)
    return {"status": "reset", "was_running": was_running}


@app.get("/api/debug/env")
def debug_env():
    """Check which environment variables are configured (does not expose values)."""
    keys_to_check = [
        "ANTHROPIC_API_KEY",
        "PERPLEXITY_API_KEY",
        "REPLICATE_API_TOKEN",
        "META_PAGE_ACCESS_TOKEN",
        "META_PAGE_ID",
        "META_IG_USER_ID",
        "DASHBOARD_URL",
    ]
    result = {}
    for key in keys_to_check:
        val = os.getenv(key, "")
        if val:
            result[key] = f"set ({len(val)} chars, starts with {val[:6]}...)"
        else:
            result[key] = "NOT SET"
    return {
        "env_status": result,
        "pipeline_running": _pipeline_running,
        "pipeline_state": get_pipeline_state(),
    }


@app.get("/api/debug/logs")
def debug_logs():
    """Get recent pipeline logs from pipeline_state.json."""
    state = get_pipeline_state()
    campaign = get_campaign_brief()
    return {
        "pipeline_state": state,
        "campaign_brief": campaign,
        "pipeline_running_flag": _pipeline_running,
    }


@app.get("/api/debug/files")
def debug_files():
    """List all output files in data/outputs/ for debugging."""
    files = []
    if OUTPUTS_DIR.exists():
        for f in sorted(OUTPUTS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat(),
            })
    images = []
    img_dir = OUTPUTS_DIR / "images"
    if img_dir.exists():
        for f in sorted(img_dir.iterdir()):
            if f.is_file():
                images.append(f.name)
    carousels_list = []
    car_dir = OUTPUTS_DIR / "carousels"
    if car_dir.exists():
        for f in sorted(car_dir.iterdir()):
            if f.is_file():
                carousels_list.append(f.name)
    return {"output_files": files, "images": images, "carousels": carousels_list}


# ── Image Regeneration ─────────────────────────────────

class RegenerateImageRequest(BaseModel):
    filename: str  # existing filename to replace
    prompt: str  # custom prompt for Flux (visual only, no text)
    width: int = 1080
    height: int = 1080
    text_overlays: list[dict] = []  # optional: [{text, position, font_size, color}]
    target: str = "images"  # "images" or "carousels"


@app.post("/api/images/regenerate")
def regenerate_image(req: RegenerateImageRequest):
    """Regenerate a single image with a custom prompt via Flux + optional text overlay."""
    import threading

    api_token = os.getenv("REPLICATE_API_TOKEN", "")
    if not api_token or "xxxxx" in api_token:
        raise HTTPException(400, "REPLICATE_API_TOKEN not configured")

    if len(req.prompt.strip()) < 5:
        raise HTTPException(400, "Prompt must be at least 5 characters")

    # Determine output dir
    if req.target == "carousels":
        output_dir = OUTPUTS_DIR / "carousels"
    else:
        output_dir = OUTPUTS_DIR / "images"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / req.filename

    def _regen():
        import httpx
        import replicate
        try:
            logger.info("Regenerating image: %s with prompt: %s", req.filename, req.prompt[:100])
            output = replicate.run(
                "black-forest-labs/flux-1.1-pro",
                input={
                    "prompt": req.prompt,
                    "width": req.width,
                    "height": req.height,
                    "output_format": "png",
                    "prompt_upsampling": True,
                },
            )
            img_url = str(output)
            img_response = httpx.get(img_url, timeout=60)
            img_response.raise_for_status()
            output_path.write_bytes(img_response.content)
            logger.info("Image regenerated: %s", output_path)

            # Apply text overlays if provided
            if req.text_overlays:
                try:
                    from utils.image_text import add_text_overlay
                    add_text_overlay(str(output_path), req.text_overlays)
                    logger.info("Text overlay applied to regenerated image: %s", req.filename)
                except Exception as te:
                    logger.error("Text overlay failed on regen: %s", te)

        except Exception as e:
            logger.error("Regeneration failed for %s: %s", req.filename, e)

    # Run in background thread so the API responds immediately
    thread = threading.Thread(target=_regen, daemon=True)
    thread.start()

    return {
        "status": "regenerating",
        "filename": req.filename,
        "prompt": req.prompt[:200],
        "message": "Image is being regenerated. Refresh in a few seconds to see the result.",
    }


# ── Templates & Brand Assets ───────────────────────────

@app.get("/api/templates")
def list_templates():
    """List all uploaded templates (images, carousels, logos, fonts)."""
    result = {"templates": [], "brand_assets": [], "fonts": []}

    # Templates
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    for f in sorted(TEMPLATES_DIR.iterdir()):
        if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".svg", ".psd"):
            result["templates"].append({
                "name": f.name,
                "size": f.stat().st_size,
                "type": f.suffix.lower(),
                "url": f"/api/templates/file/{f.name}",
                "modified": datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat(),
            })

    # Brand assets (logos, etc.)
    BRAND_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for f in sorted(BRAND_ASSETS_DIR.iterdir()):
        if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".svg"):
            result["brand_assets"].append({
                "name": f.name,
                "size": f.stat().st_size,
                "type": f.suffix.lower(),
                "url": f"/api/brand-assets/{f.name}",
            })

    # Fonts
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    for f in sorted(FONTS_DIR.iterdir()):
        if f.is_file() and f.suffix.lower() in (".ttf", ".otf", ".woff", ".woff2"):
            result["fonts"].append({
                "name": f.name,
                "size": f.stat().st_size,
            })

    return result


@app.post("/api/templates/upload")
async def upload_template(
    file: UploadFile = File(...),
    category: str = Form("template"),  # "template", "logo", "font"
):
    """Upload a template image, logo, or font file."""
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    ext = Path(file.filename).suffix.lower()

    # Determine destination
    if category == "font":
        if ext not in (".ttf", ".otf", ".woff", ".woff2"):
            raise HTTPException(400, f"Invalid font format: {ext}. Use .ttf, .otf, .woff, or .woff2")
        dest_dir = FONTS_DIR
    elif category == "logo":
        if ext not in (".png", ".jpg", ".jpeg", ".svg"):
            raise HTTPException(400, f"Invalid image format: {ext}. Use .png, .jpg, or .svg")
        dest_dir = BRAND_ASSETS_DIR
    else:  # template
        if ext not in (".png", ".jpg", ".jpeg", ".svg", ".psd"):
            raise HTTPException(400, f"Invalid format: {ext}. Use .png, .jpg, .svg, or .psd")
        dest_dir = TEMPLATES_DIR

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / file.filename

    # Save file
    content = await file.read()
    dest_path.write_bytes(content)

    logger.info("Uploaded %s to %s (%d bytes)", file.filename, category, len(content))

    return {
        "status": "uploaded",
        "filename": file.filename,
        "category": category,
        "size": len(content),
        "path": str(dest_path.relative_to(PROJECT_ROOT)),
    }


@app.delete("/api/templates/{filename}")
def delete_template(filename: str, category: str = "template"):
    """Delete a template, logo, or font file."""
    if category == "font":
        file_path = FONTS_DIR / filename
    elif category == "logo":
        file_path = BRAND_ASSETS_DIR / filename
    else:
        file_path = TEMPLATES_DIR / filename

    if not file_path.exists():
        raise HTTPException(404, f"File not found: {filename}")

    file_path.unlink()
    return {"status": "deleted", "filename": filename}


@app.get("/api/templates/file/{filename:path}")
def serve_template(filename: str):
    """Serve a template file."""
    file_path = TEMPLATES_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(404, "Template not found")
    ext = file_path.suffix.lower()
    media_types = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml"}
    return FileResponse(file_path, media_type=media_types.get(ext, "application/octet-stream"))


@app.get("/api/brand-assets/{filename:path}")
def serve_brand_asset(filename: str):
    """Serve a brand asset (logo, etc.)."""
    file_path = BRAND_ASSETS_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(404, "Brand asset not found")
    ext = file_path.suffix.lower()
    media_types = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml"}
    return FileResponse(file_path, media_type=media_types.get(ext, "application/octet-stream"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
