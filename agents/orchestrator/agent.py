"""
Orchestrator Agent - Director del pipeline de contenido.
Coordina la ejecución de todos los agentes en el orden correcto.

Nota: La orquestación principal se maneja desde main.py (CLI).
Este módulo proporciona una clase que puede coordinar programáticamente.
"""

import importlib
import traceback

from rich.console import Console
from rich.panel import Panel

from agents.base import BaseAgent
from utils.helpers import save_json
from utils.logger import setup_logger

console = Console()

# Mapeo de agentes a sus módulos y clases
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

PHASES = {
    1: {"name": "Investigación", "agents": ["trend_researcher", "viral_analyzer"]},
    2: {"name": "Planificación", "agents": ["content_planner"], "checkpoint": True},
    3: {"name": "Creación de Contenido", "agents": ["copywriter", "seo_hashtag_specialist"]},
    4: {"name": "Producción Visual", "agents": ["visual_designer", "carousel_creator"]},
    5: {"name": "Validación", "agents": ["brand_guardian"], "checkpoint": True},
    6: {"name": "Publicación", "agents": ["scheduler"], "checkpoint": True},
    7: {"name": "Análisis", "agents": ["engagement_analyst"]},
}


class OrchestratorAgent(BaseAgent):
    name = "orchestrator"
    description = "Coordina todo el pipeline de generación de contenido"

    def _run_single_agent(self, agent_name: str) -> dict:
        """Instancia y ejecuta un agente, retorna resultado y estado."""
        if agent_name not in AGENT_REGISTRY:
            return {"agent": agent_name, "status": "error", "error": f"Agent not found: {agent_name}"}

        module_path, class_name = AGENT_REGISTRY[agent_name]
        try:
            module = importlib.import_module(module_path)
            agent_class = getattr(module, class_name)
            agent_instance = agent_class()

            console.print(f"[cyan]>> Running {agent_name}...[/cyan]")
            result = agent_instance.run()
            console.print(f"[green]OK {agent_name} completed[/green]")

            return {"agent": agent_name, "status": "completed", "result_length": len(result) if result else 0}
        except Exception as e:
            self.logger.error(f"Agent {agent_name} failed: {e}\n{traceback.format_exc()}")
            console.print(f"[red]FAIL {agent_name} failed: {e}[/red]")
            return {"agent": agent_name, "status": "error", "error": str(e)}

    def run_pipeline(self, skip_checkpoints: bool = False) -> dict:
        """Ejecuta el pipeline completo fase por fase."""
        self.logger.info("Starting Content Engine Pipeline")
        console.print(Panel(
            "[bold]A&J Phygital Group Content Engine[/bold]\nAutomate. Grow. Dominate.",
            style="bold blue",
        ))

        pipeline_results = {"phases": {}, "errors": [], "status": "completed"}

        for phase_num in sorted(PHASES.keys()):
            phase_info = PHASES[phase_num]
            console.print(f"\n[bold blue]=== FASE {phase_num}: {phase_info['name']} ===[/bold blue]")

            phase_results = []
            for agent_name in phase_info["agents"]:
                result = self._run_single_agent(agent_name)
                phase_results.append(result)
                if result["status"] == "error":
                    pipeline_results["errors"].append(result)

            pipeline_results["phases"][phase_num] = {
                "name": phase_info["name"],
                "results": phase_results,
            }

            # Update pipeline state
            self.update_pipeline_state({
                "phase": phase_num,
                "phase_name": phase_info["name"],
                "agents_completed": [r["agent"] for r in phase_results if r["status"] == "completed"],
            })

            # Checkpoint
            if phase_info.get("checkpoint") and not skip_checkpoints:
                console.print("[yellow]CHECKPOINT: Requiere aprobacion humana.[/yellow]")
                try:
                    import typer
                    proceed = typer.confirm("¿Aprobar y continuar?")
                    if not proceed:
                        console.print("[red]Pipeline detenido por el usuario.[/red]")
                        pipeline_results["status"] = "stopped_by_user"
                        break
                except Exception:
                    console.print("[yellow]Running non-interactively, skipping checkpoint.[/yellow]")

        # Save final pipeline state
        state_path = self.project_root / "data" / "outputs" / "pipeline_state.json"
        save_json(pipeline_results, state_path)

        if pipeline_results["status"] == "completed":
            console.print(Panel("[bold green]Pipeline completado![/bold green]", style="green"))
        self.logger.info(f"Pipeline finished: {pipeline_results['status']}")
        return pipeline_results

    def run(self, custom_prompt: str | None = None) -> str:
        """Compatibilidad con BaseAgent.run() - ejecuta el pipeline."""
        result = self.run_pipeline()
        return f"Pipeline {result['status']}. Errors: {len(result['errors'])}"

    def _build_prompt(self) -> str:
        return "Execute the full content generation pipeline."


def main():
    agent = OrchestratorAgent()
    agent.run_pipeline()


if __name__ == "__main__":
    main()
