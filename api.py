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
from fastapi import FastAPI, HTTPException
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


# ── Models ──────────────────────────────────────────────

class CampaignRequest(BaseModel):
    brief: str
    platforms: list[str] = ["instagram", "tiktok", "linkedin", "youtube", "facebook"]
    language: list[str] = ["es", "en"]


class ApprovalRequest(BaseModel):
    checkpoint: str
    item_id: str
    decision: str  # approved, rejected, revision
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

    data["decisions"].append({
        "checkpoint": req.checkpoint,
        "item_id": req.item_id,
        "decision": req.decision,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
