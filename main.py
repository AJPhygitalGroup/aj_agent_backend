"""
A&J Phygital Group - Content Engine
Entry point principal del pipeline de generación de contenido.

Uso:
    python main.py pipeline              # Pipeline completo
    python main.py agent trend_researcher  # Un agente específico
    python main.py phase 1               # Una fase específica
    python main.py status                # Estado del pipeline
"""

import sys
from pathlib import Path

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, str(Path(__file__).parent))

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(help="A&J Phygital Group Content Engine")
console = Console()

AGENT_CLASSES = {
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

PHASES = {
    1: {"name": "Investigación", "agents": ["trend_researcher", "viral_analyzer"]},
    2: {"name": "Planificación", "agents": ["content_planner"], "checkpoint": True},
    3: {"name": "Creación de Contenido", "agents": ["copywriter", "seo_hashtag_specialist"]},
    4: {"name": "Producción Visual", "agents": ["visual_designer", "carousel_creator"]},
    5: {"name": "Validación", "agents": ["brand_guardian"], "checkpoint": True},
    6: {"name": "Publicación", "agents": ["scheduler"], "checkpoint": True},
    7: {"name": "Análisis", "agents": ["engagement_analyst"]},
}


def _run_agent(agent_name: str) -> str:
    """Instancia y ejecuta un agente."""
    if agent_name not in AGENT_CLASSES:
        console.print(f"[red]Agent '{agent_name}' not found.[/red]")
        console.print(f"Available: {', '.join(AGENT_CLASSES.keys())}")
        return ""

    module_path, class_name = AGENT_CLASSES[agent_name]
    import importlib
    module = importlib.import_module(module_path)
    agent_class = getattr(module, class_name)
    agent_instance = agent_class()

    console.print(f"[cyan]>> Running {agent_name}...[/cyan]")
    result = agent_instance.run()
    console.print(f"[green]OK {agent_name} completed[/green]")
    return result


@app.command()
def pipeline():
    """Ejecutar el pipeline completo (fase por fase)."""
    console.print(Panel(
        "[bold]A&J Phygital Group Content Engine[/bold]\nAutomate. Grow. Dominate.",
        style="bold blue",
    ))

    for phase_num in sorted(PHASES.keys()):
        phase_info = PHASES[phase_num]
        console.print(f"\n[bold blue]=== FASE {phase_num}: {phase_info['name']} ===[/bold blue]")

        for agent_name in phase_info["agents"]:
            _run_agent(agent_name)

        if phase_info.get("checkpoint"):
            console.print("[yellow]CHECKPOINT: Requiere aprobacion humana.[/yellow]")
            proceed = typer.confirm("¿Aprobar y continuar?")
            if not proceed:
                console.print("[red]Pipeline detenido por el usuario.[/red]")
                return

    console.print(Panel("[bold green]Pipeline completado![/bold green]", style="green"))


@app.command()
def agent(name: str = typer.Argument(help="Nombre del agente")):
    """Ejecutar un agente específico."""
    _run_agent(name)


@app.command()
def phase(number: int = typer.Argument(help="Número de fase (1-7)")):
    """Ejecutar una fase específica del pipeline."""
    if number not in PHASES:
        console.print(f"[red]Phase {number} not found. Available: 1-7[/red]")
        return
    phase_info = PHASES[number]
    console.print(Panel(f"FASE {number}: {phase_info['name']}", style="bold blue"))
    for agent_name in phase_info["agents"]:
        _run_agent(agent_name)


@app.command()
def status():
    """Ver estado del pipeline."""
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
        console.print("[yellow]No pipeline state. Run the pipeline first.[/yellow]")


@app.command(name="list")
def agents_list():
    """Listar agentes disponibles."""
    table = Table(title="Available Agents")
    table.add_column("#", style="cyan")
    table.add_column("Agent", style="green")
    for i, name in enumerate(AGENT_CLASSES.keys(), 1):
        table.add_row(str(i), name)
    console.print(table)


@app.command()
def phases():
    """Listar fases del pipeline."""
    table = Table(title="Pipeline Phases")
    table.add_column("Phase", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Agents", style="white")
    table.add_column("Checkpoint", style="red")
    for num, info in PHASES.items():
        table.add_row(str(num), info["name"], ", ".join(info["agents"]),
                       "Yes" if info.get("checkpoint") else "")
    console.print(table)


if __name__ == "__main__":
    app()
