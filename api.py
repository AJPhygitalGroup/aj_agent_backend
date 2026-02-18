"""
A&J Phygital Group - Content Engine API
FastAPI backend que expone los agentes como endpoints REST.
Se despliega en el VPS con Docker/Easypanel.
"""

import json
import os
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent))

from utils.helpers import get_project_root, load_json, save_json

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

    from agents.orchestrator.agent import OrchestratorAgent, PHASES
    import importlib

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

        # Run phases
        for phase_num in sorted(PHASES.keys()):
            phase_info = PHASES[phase_num]

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
                    continue
                module_path, class_name = AGENT_REGISTRY[agent_name]
                try:
                    module = importlib.import_module(module_path)
                    agent_class = getattr(module, class_name)
                    agent_instance = agent_class()
                    agent_instance.run()
                except Exception as e:
                    print(f"Agent {agent_name} failed: {e}")

            # Checkpoints - pause and wait for approval via API
            if phase_info.get("checkpoint"):
                save_json({
                    "status": "waiting_approval",
                    "phase": phase_num,
                    "phase_name": phase_info["name"],
                    "checkpoint": True,
                    "campaign_brief": brief,
                    "started_at": campaign_data["timestamp"],
                }, OUTPUTS_DIR / "pipeline_state.json")

                # Wait for approval (poll every 5 seconds)
                import time
                while True:
                    state = get_pipeline_state()
                    if state.get("status") == "approved":
                        # Reset to running
                        save_json({
                            "status": "running",
                            "phase": phase_num,
                            "phase_name": phase_info["name"],
                            "campaign_brief": brief,
                            "started_at": campaign_data["timestamp"],
                        }, OUTPUTS_DIR / "pipeline_state.json")
                        break
                    elif state.get("status") == "stopped_by_user":
                        campaign_data["status"] = "stopped"
                        save_json(campaign_data, INPUTS_DIR / "campaign_brief.json")
                        return
                    time.sleep(5)

        # Completed
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
        print(f"Pipeline error: {e}")
        save_json({
            "status": "error",
            "error": str(e),
            "campaign_brief": brief,
        }, OUTPUTS_DIR / "pipeline_state.json")
    finally:
        with _pipeline_lock:
            _pipeline_running = False


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
            raise HTTPException(409, "A campaign is already running")
        _pipeline_running = True

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
