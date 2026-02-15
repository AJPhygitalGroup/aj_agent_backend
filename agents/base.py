"""
Clase base para todos los agentes del Content Engine.
Cada agente hereda de BaseAgent para tener acceso a configuración,
logging, y helpers comunes.
"""

import json
from pathlib import Path
from typing import Any

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


class BaseAgent:
    """Clase base para todos los agentes."""

    name: str = "base"
    description: str = ""

    def __init__(self):
        self.logger = setup_logger(self.name)
        self.config = get_config()
        self.brand = get_brand_config()
        self.platforms = get_platform_config()
        self.project_root = get_project_root()
        self.output_dirs = ensure_output_dirs()

    def load_prompt(self) -> str:
        """Carga el system prompt del agente desde prompts/."""
        prompt_path = self.project_root / "prompts" / f"{self.name}.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        self.logger.warning(f"Prompt file not found: {prompt_path}")
        return ""

    def save_output(self, data: Any, suffix: str = "output") -> Path:
        """Guarda el output del agente como JSON."""
        filename = timestamp_filename(self.name, suffix)
        output_path = self.project_root / "data" / "outputs" / filename
        save_json(data if isinstance(data, dict) else data.model_dump(), output_path)
        self.logger.info(f"Output saved: {output_path}")
        return output_path

    def load_latest_output(self, agent_name: str) -> dict | None:
        """Carga el output más reciente de otro agente."""
        outputs_dir = self.project_root / "data" / "outputs"
        files = sorted(
            outputs_dir.glob(f"{agent_name}_*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        if files:
            return load_json(files[0])
        self.logger.warning(f"No output found for agent: {agent_name}")
        return None

    def get_pipeline_state(self) -> dict:
        """Lee el estado actual del pipeline."""
        state_path = self.project_root / "data" / "outputs" / "pipeline_state.json"
        if state_path.exists():
            return load_json(state_path)
        return {"phase": "idle", "agents_completed": [], "errors": []}

    def update_pipeline_state(self, updates: dict) -> None:
        """Actualiza el estado del pipeline."""
        state = self.get_pipeline_state()
        state.update(updates)
        state_path = self.project_root / "data" / "outputs" / "pipeline_state.json"
        save_json(state, state_path)
