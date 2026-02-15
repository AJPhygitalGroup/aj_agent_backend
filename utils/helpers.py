"""
Funciones de utilidad compartidas entre agentes.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


def generate_id(prefix: str = "slot") -> str:
    """Genera un ID único para contenido."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    short_uuid = uuid.uuid4().hex[:6]
    return f"{prefix}_{timestamp}_{short_uuid}"


def load_yaml(file_path: str | Path) -> dict:
    """Carga un archivo YAML."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_json(data: Any, file_path: str | Path, indent: int = 2) -> None:
    """Guarda datos como JSON."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)


def load_json(file_path: str | Path) -> Any:
    """Carga un archivo JSON."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_project_root() -> Path:
    """Retorna la raíz del proyecto."""
    return Path(__file__).parent.parent


def get_config() -> dict:
    """Carga la configuración principal."""
    config_path = get_project_root() / "config" / "config.yaml"
    return load_yaml(config_path)


def get_brand_config() -> dict:
    """Carga la configuración de marca."""
    brand_path = get_project_root() / "config" / "brand.yaml"
    return load_yaml(brand_path)


def get_platform_config() -> dict:
    """Carga la configuración de plataformas."""
    platform_path = get_project_root() / "config" / "platforms.yaml"
    return load_yaml(platform_path)


def ensure_output_dirs() -> dict[str, Path]:
    """Crea y retorna los directorios de output."""
    root = get_project_root()
    dirs = {
        "images": root / "data" / "outputs" / "images",
        "videos": root / "data" / "outputs" / "videos",
        "carousels": root / "data" / "outputs" / "carousels",
        "scripts": root / "data" / "outputs" / "scripts",
        "temp": root / "data" / "temp",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def timestamp_filename(agent_name: str, content_type: str, ext: str = "json") -> str:
    """Genera nombre de archivo con timestamp."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{agent_name}_{ts}_{content_type}.{ext}"
