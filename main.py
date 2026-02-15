"""
A&J Phygital Group - Content Engine
Entry point principal del pipeline de generación de contenido.

Uso:
    python main.py                    # Ejecutar pipeline completo
    python main.py --agent <nombre>   # Ejecutar un agente específico
    python main.py --phase <numero>   # Ejecutar una fase específica
"""

import asyncio
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

app = typer.Typer(help="A&J Phygital Group Content Engine")
console = Console()

AGENTS = {
    "orchestrator": "agents.orchestrator.agent",
    "trend_researcher": "agents.trend_researcher.agent",
    "viral_analyzer": "agents.viral_analyzer.agent",
    "content_planner": "agents.content_planner.agent",
    "copywriter": "agents.copywriter.agent",
    "seo_hashtag_specialist": "agents.seo_hashtag_specialist.agent",
    "visual_designer": "agents.visual_designer.agent",
    "carousel_creator": "agents.carousel_creator.agent",
    "avatar_video_producer": "agents.avatar_video_producer.agent",
    "brand_guardian": "agents.brand_guardian.agent",
    "scheduler": "agents.scheduler.agent",
    "engagement_analyst": "agents.engagement_analyst.agent",
}

PHASES = {
    1: {"name": "Investigación", "agents": ["trend_researcher", "viral_analyzer"], "parallel": True},
    2: {"name": "Planificación", "agents": ["content_planner"], "checkpoint": True},
    3: {"name": "Creación de Contenido", "agents": ["copywriter", "seo_hashtag_specialist"], "parallel": True},
    4: {"name": "Producción Visual", "agents": ["visual_designer", "carousel_creator"], "parallel": True},
    5: {"name": "Validación", "agents": ["brand_guardian"], "checkpoint": True},
    6: {"name": "Publicación", "agents": ["scheduler"], "checkpoint": True},
    7: {"name": "Análisis", "agents": ["engagement_analyst"]},
}


async def run_agent(agent_name: str) -> None:
    """Ejecuta un agente específico."""
    module_path = AGENTS.get(agent_name)
    if not module_path:
        console.print(f"[red]Agent '{agent_name}' not found.[/red]")
        console.print(f"Available agents: {', '.join(AGENTS.keys())}")
        return

    import importlib
    module = importlib.import_module(module_path)
    await module.main()


async def run_phase(phase_num: int) -> None:
    """Ejecuta una fase del pipeline."""
    phase = PHASES.get(phase_num)
    if not phase:
        console.print(f"[red]Phase {phase_num} not found. Available: 1-7[/red]")
        return

    console.print(Panel(f"FASE {phase_num}: {phase['name']}", style="bold blue"))
    agents = phase["agents"]

    if phase.get("parallel") and len(agents) > 1:
        console.print(f"[cyan]Running {len(agents)} agents in parallel...[/cyan]")
        tasks = [run_agent(a) for a in agents]
        await asyncio.gather(*tasks)
    else:
        for agent_name in agents:
            console.print(f"[cyan]Running {agent_name}...[/cyan]")
            await run_agent(agent_name)

    if phase.get("checkpoint"):
        console.print("[yellow]CHECKPOINT: Human approval required. Check the dashboard.[/yellow]")


@app.command()
def pipeline():
    """Ejecutar el pipeline completo via el Orchestrator."""
    console.print(Panel(
        "[bold]A&J Phygital Group Content Engine[/bold]\n"
        "Automate. Grow. Dominate.",
        style="bold blue",
    ))
    asyncio.run(run_agent("orchestrator"))


@app.command()
def agent(name: str = typer.Argument(help="Nombre del agente a ejecutar")):
    """Ejecutar un agente específico."""
    console.print(f"[cyan]Running agent: {name}[/cyan]")
    asyncio.run(run_agent(name))


@app.command()
def phase(number: int = typer.Argument(help="Número de fase (1-7)")):
    """Ejecutar una fase específica del pipeline."""
    asyncio.run(run_phase(number))


@app.command()
def status():
    """Ver el estado actual del pipeline."""
    from utils.helpers import get_project_root, load_json

    state_path = get_project_root() / "data" / "outputs" / "pipeline_state.json"
    if state_path.exists():
        state = load_json(state_path)
        table = Table(title="Pipeline Status")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        for key, value in state.items():
            table.add_row(key, str(value))
        console.print(table)
    else:
        console.print("[yellow]No pipeline state found. Run the pipeline first.[/yellow]")


@app.command()
def agents_list():
    """Listar todos los agentes disponibles."""
    table = Table(title="Available Agents")
    table.add_column("#", style="cyan")
    table.add_column("Agent", style="green")
    table.add_column("Module", style="dim")

    for i, (name, module) in enumerate(AGENTS.items(), 1):
        table.add_row(str(i), name, module)

    console.print(table)


@app.command()
def phases_list():
    """Listar todas las fases del pipeline."""
    table = Table(title="Pipeline Phases")
    table.add_column("Phase", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Agents", style="white")
    table.add_column("Parallel", style="yellow")
    table.add_column("Checkpoint", style="red")

    for num, phase in PHASES.items():
        table.add_row(
            str(num),
            phase["name"],
            ", ".join(phase["agents"]),
            "Yes" if phase.get("parallel") else "No",
            "Yes" if phase.get("checkpoint") else "No",
        )

    console.print(table)


if __name__ == "__main__":
    app()
