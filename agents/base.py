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
    model: str = "claude-sonnet-4-20250514"
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
                self.logger.info(f"Output saved: {output_path}")
                return f"Output saved to: {output_path}"

            elif tool_name == "search_perplexity":
                return self._search_perplexity(tool_input["query"])

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

    # ── Agentic Loop ───────────────────────────────────────

    def run(self, custom_prompt: str | None = None) -> str:
        """Ejecuta el agente con un agentic loop (tool_use loop)."""
        system_prompt = self.load_prompt()
        user_prompt = custom_prompt or self._build_prompt()
        tools = self.get_tools()
        messages = [{"role": "user", "content": user_prompt}]

        self.logger.info(f"Starting agentic loop (max {self.max_turns} turns)")
        final_text = ""

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

        self.logger.info("Agentic loop finished")
        return final_text

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
