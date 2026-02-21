"""
Clase base para todos los agentes del Content Engine.
Usa la API de Anthropic directamente con tool_use para agentic loops.
"""

import json
import os
from pathlib import Path
from typing import Any

import anthropic
import httpx
from dotenv import load_dotenv

from utils.helpers import (
    ensure_output_dirs,
    get_brand_config,
    get_config,
    get_platform_config,
    get_project_root,
    load_json,
    save_json,
    timestamp_filename,
)
from utils.logger import setup_logger

load_dotenv(get_project_root() / ".env", override=True)


class BaseAgent:
    """Clase base con agentic loop usando Anthropic API directamente."""

    name: str = "base"
    description: str = ""
    # Default model — agents can override. Use Haiku for simple tasks, Sonnet for creative.
    model: str = "claude-haiku-4-20250514"
    max_turns: int = 25

    def __init__(self):
        self.logger = setup_logger(self.name)
        self.config = get_config()
        self.brand = get_brand_config()
        self.platforms = get_platform_config()
        self.project_root = get_project_root()
        self.output_dirs = ensure_output_dirs()
        self.client = anthropic.Anthropic()

    def load_prompt(self) -> str:
        prompt_path = self.project_root / "prompts" / f"{self.name}.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        self.logger.warning(f"Prompt file not found: {prompt_path}")
        return ""

    # ── Tools ──────────────────────────────────────────────

    def get_tools(self) -> list[dict]:
        """Override en cada agente para agregar tools específicos."""
        return self._common_tools()

    def _common_tools(self) -> list[dict]:
        return [
            {
                "name": "get_brand_guidelines",
                "description": "Get complete brand guidelines (colors, voice, services, pillars, personas, CTAs).",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "get_platform_specs",
                "description": "Get specs for all platforms (resolutions, limits, formats, rate limits).",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "read_agent_output",
                "description": "Read the latest output from another agent in the pipeline.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string", "description": "Agent name (e.g. trend_researcher, viral_analyzer)"},
                    },
                    "required": ["agent_name"],
                },
            },
            {
                "name": "save_agent_output",
                "description": "Save this agent's output as JSON to data/outputs/.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "output_data": {"type": "string", "description": "JSON string of the output"},
                        "suffix": {"type": "string", "description": "File suffix (e.g. trend_report, content_plan)"},
                    },
                    "required": ["output_data", "suffix"],
                },
            },
            {
                "name": "search_perplexity",
                "description": "Search the web using Perplexity AI for real-time information, trends, and research.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query in English or Spanish"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "list_templates",
                "description": (
                    "List uploaded brand templates and assets. "
                    "Returns available templates (image backgrounds, layouts), logos, and fonts "
                    "that should be used to maintain brand identity."
                ),
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
        ]

    def handle_tool_call(self, tool_name: str, tool_input: dict) -> str:
        """Procesa un tool call y retorna resultado como string."""
        try:
            if tool_name == "get_brand_guidelines":
                return json.dumps(self.brand, ensure_ascii=False, default=str)

            elif tool_name == "get_platform_specs":
                return json.dumps(self.platforms, ensure_ascii=False, default=str)

            elif tool_name == "read_agent_output":
                agent_name = tool_input["agent_name"]
                outputs_dir = self.project_root / "data" / "outputs"
                files = sorted(
                    outputs_dir.glob(f"{agent_name}_*.json"),
                    key=lambda f: f.stat().st_mtime,
                    reverse=True,
                )
                if files:
                    data = load_json(files[0])
                    return json.dumps(data, ensure_ascii=False, default=str)
                return f"No output found for agent: {agent_name}"

            elif tool_name == "save_agent_output":
                output_data = tool_input["output_data"]
                suffix = tool_input.get("suffix", "output")
                try:
                    parsed = json.loads(output_data)
                except (json.JSONDecodeError, TypeError):
                    parsed = {"raw_output": output_data}
                filename = timestamp_filename(self.name, suffix)
                output_path = self.project_root / "data" / "outputs" / filename
                save_json(parsed, output_path)
                self._output_saved = True  # Mark that output was saved
                self.logger.info(f"Output saved: {output_path}")
                return f"Output saved to: {output_path}"

            elif tool_name == "search_perplexity":
                return self._search_perplexity(tool_input["query"])

            elif tool_name == "list_templates":
                return self._list_templates()

            else:
                return self.handle_custom_tool(tool_name, tool_input)

        except Exception as e:
            self.logger.error(f"Tool error [{tool_name}]: {e}")
            return f"Error: {str(e)}"

    def handle_custom_tool(self, tool_name: str, tool_input: dict) -> str:
        """Override en agentes hijos para tools específicos."""
        return f"Unknown tool: {tool_name}"

    def _search_perplexity(self, query: str) -> str:
        api_key = os.getenv("PERPLEXITY_API_KEY", "")
        if not api_key or "xxxxx" in api_key:
            return f"[Perplexity not configured] Query: {query}"
        try:
            response = httpx.post(
                "https://api.perplexity.ai/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": "sonar", "messages": [{"role": "user", "content": query}]},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            self.logger.error(f"Perplexity error: {e}")
            return f"Search error: {str(e)}"

    def _list_templates(self) -> str:
        """List available templates, brand assets, and fonts."""
        result = {"templates": [], "logos": [], "fonts": [], "has_templates": False}

        templates_dir = self.project_root / "data" / "inputs" / "templates"
        brand_dir = self.project_root / "data" / "brand_assets"
        fonts_dir = brand_dir / "fonts"

        # Templates
        if templates_dir.exists():
            for f in sorted(templates_dir.iterdir()):
                if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".svg"):
                    result["templates"].append({
                        "filename": f.name,
                        "path": str(f),
                        "type": f.suffix.lower(),
                    })

        # Brand logos
        if brand_dir.exists():
            for f in sorted(brand_dir.iterdir()):
                if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".svg"):
                    result["logos"].append({
                        "filename": f.name,
                        "path": str(f),
                    })

        # Fonts
        if fonts_dir.exists():
            for f in sorted(fonts_dir.iterdir()):
                if f.is_file() and f.suffix.lower() in (".ttf", ".otf"):
                    result["fonts"].append(f.name)

        result["has_templates"] = len(result["templates"]) > 0
        result["has_logos"] = len(result["logos"]) > 0
        result["has_fonts"] = len(result["fonts"]) > 0

        return json.dumps(result, ensure_ascii=False)

    # ── Campaign Brief ────────────────────────────────────

    def get_campaign_brief(self) -> dict | None:
        """Lee el brief de campaña activo desde data/inputs/campaign_brief.json."""
        brief_path = self.project_root / "data" / "inputs" / "campaign_brief.json"
        if brief_path.exists():
            try:
                return load_json(brief_path)
            except Exception:
                return None
        return None

    def _inject_campaign_context(self, prompt: str) -> str:
        """Si hay un campaign brief activo, lo inyecta como contexto adicional al prompt."""
        brief = self.get_campaign_brief()
        if not brief or brief.get("status") not in ("running", None):
            return prompt

        campaign_context = f"""
## CAMPAIGN BRIEF (CONTEXTO DE LA CAMPAÑA ACTIVA)
El usuario ha solicitado la siguiente campaña. ADAPTA todo tu trabajo a este brief:

**Brief:** {brief.get('brief', 'No especificado')}
**Plataformas objetivo:** {', '.join(brief.get('platforms', []))}
**Idiomas:** {', '.join(brief.get('language', ['es', 'en']))}

IMPORTANTE: Tu investigación, contenido y recomendaciones deben estar 100% enfocados
en el brief de campaña anterior. NO uses los keywords por defecto del config.yaml,
usa el brief como guía principal.
---

"""
        return campaign_context + prompt

    # ── Agentic Loop ───────────────────────────────────────

    def run(self, custom_prompt: str | None = None) -> str:
        """Ejecuta el agente con un agentic loop (tool_use loop)."""
        system_prompt = self.load_prompt()
        user_prompt = custom_prompt or self._build_prompt()
        # Inyectar contexto de campaña si existe
        user_prompt = self._inject_campaign_context(user_prompt)
        tools = self.get_tools()
        messages = [{"role": "user", "content": user_prompt}]

        self.logger.info(f"Starting agentic loop (max {self.max_turns} turns)")
        final_text = ""
        self._output_saved = False  # Track whether save_agent_output was called

        for turn in range(self.max_turns):
            self.logger.info(f"Turn {turn + 1}/{self.max_turns}")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=8096,
                system=system_prompt,
                tools=tools,
                messages=messages,
            )

            # Extraer text y tool_use blocks
            tool_calls = []
            text_parts = []
            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                    self.logger.info(f"Agent says: {block.text[:200]}")
                elif block.type == "tool_use":
                    tool_calls.append(block)
                    self.logger.info(f"Tool: {block.name}({str(block.input)[:100]})")

            # Si no hay tool calls → agente terminó
            if not tool_calls:
                final_text = "\n".join(text_parts)
                self.logger.info("Agent completed (no more tool calls)")
                break

            # Agregar respuesta del assistant
            messages.append({"role": "assistant", "content": response.content})

            # Ejecutar tools y agregar resultados
            tool_results = []
            for tc in tool_calls:
                result = self.handle_tool_call(tc.name, tc.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": result[:50000],  # Truncar si es muy largo
                })

            messages.append({"role": "user", "content": tool_results})

        # Auto-save fallback: if the LLM never called save_agent_output,
        # try to extract and save JSON from its final text response.
        if not self._output_saved and final_text:
            self.logger.warning(
                "Agent '%s' finished without calling save_agent_output. "
                "Attempting auto-save of final response.",
                self.name,
            )
            self._auto_save_output(final_text)

        self.logger.info("Agentic loop finished")
        return final_text

    def _auto_save_output(self, text: str) -> None:
        """Attempt to extract JSON from the agent's final text and save it."""
        import re

        # Try to find a JSON block in the text (```json ... ``` or raw {})
        json_data = None

        # 1. Look for ```json ... ``` blocks
        json_match = re.search(r"```json\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
        if json_match:
            try:
                json_data = json.loads(json_match.group(1))
            except (json.JSONDecodeError, TypeError):
                pass

        # 2. Try the entire text as JSON
        if json_data is None:
            try:
                json_data = json.loads(text)
            except (json.JSONDecodeError, TypeError):
                pass

        # 3. Try to find the largest {...} block
        if json_data is None:
            brace_match = re.search(r"\{[\s\S]+\}", text)
            if brace_match:
                try:
                    json_data = json.loads(brace_match.group(0))
                except (json.JSONDecodeError, TypeError):
                    pass

        # 4. Fallback: save raw text as wrapped JSON
        if json_data is None:
            json_data = {"raw_output": text, "auto_saved": True}
            self.logger.warning("Could not parse JSON from output, saving raw text")
        else:
            if isinstance(json_data, dict):
                json_data["auto_saved"] = True

        try:
            suffix = self._get_default_suffix()
            self.save_output(json_data, suffix=suffix)
            self._output_saved = True
            self.logger.info("Auto-saved output with suffix '%s'", suffix)
        except Exception as e:
            self.logger.error("Auto-save failed: %s", e)

    def _get_default_suffix(self) -> str:
        """Return a reasonable default suffix based on agent name."""
        suffix_map = {
            "trend_researcher": "trend_report",
            "viral_analyzer": "viral_analysis",
            "content_planner": "content_plan",
            "copywriter": "scripts",
            "visual_designer": "images",
            "carousel_creator": "carousels",
            "seo_hashtag_specialist": "seo_optimizations",
            "brand_guardian": "compliance",
            "scheduler": "schedule",
            "engagement_analyst": "engagement_report",
        }
        return suffix_map.get(self.name, "output")

    def _build_prompt(self) -> str:
        """Override en cada agente."""
        return "Execute your task as defined in the system prompt."

    # ── Legacy helpers ─────────────────────────────────────

    def save_output(self, data: Any, suffix: str = "output") -> Path:
        filename = timestamp_filename(self.name, suffix)
        output_path = self.project_root / "data" / "outputs" / filename
        save_json(data if isinstance(data, dict) else data.model_dump(), output_path)
        self.logger.info(f"Output saved: {output_path}")
        return output_path

    def load_latest_output(self, agent_name: str) -> dict | None:
        outputs_dir = self.project_root / "data" / "outputs"
        files = sorted(outputs_dir.glob(f"{agent_name}_*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        return load_json(files[0]) if files else None

    def get_pipeline_state(self) -> dict:
        state_path = self.project_root / "data" / "outputs" / "pipeline_state.json"
        return load_json(state_path) if state_path.exists() else {"phase": "idle", "agents_completed": [], "errors": []}

    def update_pipeline_state(self, updates: dict) -> None:
        state = self.get_pipeline_state()
        state.update(updates)
        save_json(state, self.project_root / "data" / "outputs" / "pipeline_state.json")
