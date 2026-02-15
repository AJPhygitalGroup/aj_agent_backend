"""
Sistema de logging centralizado para el Content Engine.
Usa loguru para logging estructurado con rotación de archivos.
"""

import sys
from pathlib import Path

from loguru import logger

# Directorio de logs
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logger(agent_name: str, log_level: str = "INFO") -> logger:
    """
    Configura logger para un agente específico.

    Args:
        agent_name: Nombre del agente (ej: "orchestrator", "trend_researcher")
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Logger configurado
    """
    # Remover handlers por defecto
    logger.remove()

    # Handler de consola con formato bonito
    logger.add(
        sys.stderr,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[agent]}</cyan> | "
            "<level>{message}</level>"
        ),
    )

    # Handler de archivo con rotación diaria
    logger.add(
        LOG_DIR / f"{agent_name}_{{time:YYYY-MM-DD}}.log",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[agent]} | {message}",
        rotation="00:00",  # Rotar a medianoche
        retention="30 days",
        compression="zip",
    )

    # Handler para errores en archivo separado
    logger.add(
        LOG_DIR / "errors_{time:YYYY-MM-DD}.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[agent]} | {message}",
        rotation="00:00",
        retention="30 days",
    )

    return logger.bind(agent=agent_name)


def get_pipeline_logger() -> logger:
    """Logger específico para el pipeline/orchestrator."""
    return setup_logger("pipeline")
