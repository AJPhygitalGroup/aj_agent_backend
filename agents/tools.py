"""
Custom tools compartidos para los agentes del Content Engine.
Se registran como MCP servers in-process usando el Claude Agent SDK.
"""

from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool

from utils.helpers import (
    get_brand_config,
    get_config,
    get_platform_config,
    get_project_root,
    load_json,
    save_json,
)


# ============================================================
# Tool: Leer configuración de marca
# ============================================================
@tool(
    "get_brand_guidelines",
    "Get the complete brand guidelines for A&J Phygital Group including colors, tone of voice, content pillars, buyer personas, CTAs, and services.",
    {},
)
async def get_brand_guidelines(args: dict[str, Any]) -> dict[str, Any]:
    brand = get_brand_config()
    return {"content": [{"type": "text", "text": str(brand)}]}


# ============================================================
# Tool: Leer configuración de plataformas
# ============================================================
@tool(
    "get_platform_specs",
    "Get technical specifications for all social media platforms (resolutions, character limits, formats, rate limits).",
    {},
)
async def get_platform_specs(args: dict[str, Any]) -> dict[str, Any]:
    platforms = get_platform_config()
    return {"content": [{"type": "text", "text": str(platforms)}]}


# ============================================================
# Tool: Leer/escribir estado del pipeline
# ============================================================
@tool(
    "get_pipeline_state",
    "Get the current state of the content generation pipeline (phase, completed agents, errors).",
    {},
)
async def get_pipeline_state(args: dict[str, Any]) -> dict[str, Any]:
    state_path = get_project_root() / "data" / "outputs" / "pipeline_state.json"
    if state_path.exists():
        state = load_json(state_path)
    else:
        state = {"phase": "idle", "agents_completed": [], "errors": []}
    return {"content": [{"type": "text", "text": str(state)}]}


@tool(
    "update_pipeline_state",
    "Update the pipeline state with new phase, completed agents, or errors.",
    {
        "type": "object",
        "properties": {
            "phase": {"type": "string", "description": "Current pipeline phase"},
            "agent_completed": {"type": "string", "description": "Name of agent that just completed"},
            "error": {"type": "string", "description": "Error message if any"},
        },
    },
)
async def update_pipeline_state(args: dict[str, Any]) -> dict[str, Any]:
    state_path = get_project_root() / "data" / "outputs" / "pipeline_state.json"
    if state_path.exists():
        state = load_json(state_path)
    else:
        state = {"phase": "idle", "agents_completed": [], "errors": []}

    if "phase" in args:
        state["phase"] = args["phase"]
    if "agent_completed" in args and args["agent_completed"]:
        if "agents_completed" not in state:
            state["agents_completed"] = []
        state["agents_completed"].append(args["agent_completed"])
    if "error" in args and args["error"]:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(args["error"])

    save_json(state, state_path)
    return {"content": [{"type": "text", "text": f"Pipeline state updated: {state}"}]}


# ============================================================
# Tool: Leer output de otro agente
# ============================================================
@tool(
    "read_agent_output",
    "Read the latest output from a specific agent. Use this to get data produced by other agents in the pipeline.",
    {"agent_name": str},
)
async def read_agent_output(args: dict[str, Any]) -> dict[str, Any]:
    agent_name = args["agent_name"]
    outputs_dir = get_project_root() / "data" / "outputs"
    files = sorted(
        outputs_dir.glob(f"{agent_name}_*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    if files:
        data = load_json(files[0])
        return {"content": [{"type": "text", "text": str(data)}]}
    return {"content": [{"type": "text", "text": f"No output found for agent: {agent_name}"}]}


# ============================================================
# Tool: Guardar output de un agente
# ============================================================
@tool(
    "save_agent_output",
    "Save the output of an agent as a JSON file in data/outputs/.",
    {"agent_name": str, "output_data": str, "suffix": str},
)
async def save_agent_output(args: dict[str, Any]) -> dict[str, Any]:
    import json
    from utils.helpers import timestamp_filename

    agent_name = args["agent_name"]
    suffix = args.get("suffix", "output")
    output_data = args["output_data"]

    # Parse si es string JSON
    if isinstance(output_data, str):
        try:
            output_data = json.loads(output_data)
        except json.JSONDecodeError:
            output_data = {"raw_output": output_data}

    filename = timestamp_filename(agent_name, suffix)
    output_path = get_project_root() / "data" / "outputs" / filename
    save_json(output_data, output_path)
    return {"content": [{"type": "text", "text": f"Output saved to: {output_path}"}]}


# ============================================================
# Tool: Solicitar aprobación humana
# ============================================================
@tool(
    "request_human_approval",
    "Pause the pipeline and request human approval via the dashboard. Use at checkpoints.",
    {"checkpoint_name": str, "summary": str},
)
async def request_human_approval(args: dict[str, Any]) -> dict[str, Any]:
    checkpoint = args["checkpoint_name"]
    summary = args["summary"]
    approval_path = get_project_root() / "data" / "outputs" / "pending_approval.json"
    save_json(
        {
            "checkpoint": checkpoint,
            "summary": summary,
            "status": "pending",
        },
        approval_path,
    )
    return {
        "content": [
            {
                "type": "text",
                "text": (
                    f"CHECKPOINT: {checkpoint}\n"
                    f"Summary: {summary}\n"
                    f"Status: AWAITING HUMAN APPROVAL\n"
                    f"The pipeline is paused. Waiting for approval."
                ),
            }
        ]
    }


# ============================================================
# Crear MCP Server con todos los tools compartidos
# ============================================================
def create_content_engine_tools():
    """Crea el MCP server con todos los tools del Content Engine."""
    return create_sdk_mcp_server(
        name="content-engine",
        version="1.0.0",
        tools=[
            get_brand_guidelines,
            get_platform_specs,
            get_pipeline_state,
            update_pipeline_state,
            read_agent_output,
            save_agent_output,
            request_human_approval,
        ],
    )
