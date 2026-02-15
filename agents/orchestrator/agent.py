"""
Orchestrator Agent - Director del pipeline de contenido.
Coordina la ejecución de todos los agentes en el orden correcto.
"""

import asyncio
from pathlib import Path

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, query

from agents.base import BaseAgent
from agents.tools import create_content_engine_tools


class OrchestratorAgent(BaseAgent):
    name = "orchestrator"
    description = "Coordina todo el pipeline de generación de contenido"

    def get_subagent_definitions(self) -> dict[str, AgentDefinition]:
        """Define todos los sub-agentes disponibles."""
        prompts_dir = self.project_root / "prompts"

        def load_prompt(agent_name: str) -> str:
            path = prompts_dir / f"{agent_name}.md"
            return path.read_text(encoding="utf-8") if path.exists() else ""

        return {
            "trend-researcher": AgentDefinition(
                description="Investigates trending topics across social media platforms and Google.",
                prompt=load_prompt("trend_researcher"),
                tools=["WebSearch", "WebFetch", "mcp__content-engine__save_agent_output", "mcp__content-engine__get_brand_guidelines"],
                model="sonnet",
            ),
            "viral-analyzer": AgentDefinition(
                description="Analyzes the structure, tone, music, and scripts of viral content.",
                prompt=load_prompt("viral_analyzer"),
                tools=["WebSearch", "WebFetch", "mcp__content-engine__read_agent_output", "mcp__content-engine__save_agent_output"],
                model="sonnet",
            ),
            "content-planner": AgentDefinition(
                description="Creates weekly content plans and exports to Google Sheets.",
                prompt=load_prompt("content_planner"),
                tools=[
                    "mcp__content-engine__read_agent_output",
                    "mcp__content-engine__save_agent_output",
                    "mcp__content-engine__get_brand_guidelines",
                    "mcp__content-engine__get_platform_specs",
                ],
                model="sonnet",
            ),
            "copywriter": AgentDefinition(
                description="Writes scripts, captions, and descriptions for all content types.",
                prompt=load_prompt("copywriter"),
                tools=[
                    "mcp__content-engine__read_agent_output",
                    "mcp__content-engine__save_agent_output",
                    "mcp__content-engine__get_brand_guidelines",
                ],
                model="opus",
            ),
            "seo-specialist": AgentDefinition(
                description="Optimizes SEO, hashtags, and keywords for maximum reach.",
                prompt=load_prompt("seo_hashtag_specialist"),
                tools=[
                    "WebSearch",
                    "mcp__content-engine__read_agent_output",
                    "mcp__content-engine__save_agent_output",
                    "mcp__content-engine__get_brand_guidelines",
                ],
                model="sonnet",
            ),
            "visual-designer": AgentDefinition(
                description="Generates hook images and thumbnails using Flux API.",
                prompt=load_prompt("visual_designer"),
                tools=[
                    "mcp__content-engine__read_agent_output",
                    "mcp__content-engine__save_agent_output",
                    "mcp__content-engine__get_brand_guidelines",
                    "Bash",
                ],
                model="sonnet",
            ),
            "carousel-creator": AgentDefinition(
                description="Creates carousel posts for Instagram and LinkedIn.",
                prompt=load_prompt("carousel_creator"),
                tools=[
                    "mcp__content-engine__read_agent_output",
                    "mcp__content-engine__save_agent_output",
                    "mcp__content-engine__get_brand_guidelines",
                    "Bash",
                ],
                model="sonnet",
            ),
            "avatar-video-producer": AgentDefinition(
                description="Generates AI avatar videos using HeyGen API. Only activated on demand.",
                prompt=load_prompt("avatar_video_producer"),
                tools=[
                    "mcp__content-engine__read_agent_output",
                    "mcp__content-engine__save_agent_output",
                    "Bash",
                ],
                model="sonnet",
            ),
            "brand-guardian": AgentDefinition(
                description="Validates all content against brand guidelines before publishing.",
                prompt=load_prompt("brand_guardian"),
                tools=[
                    "mcp__content-engine__read_agent_output",
                    "mcp__content-engine__save_agent_output",
                    "mcp__content-engine__get_brand_guidelines",
                ],
                model="opus",
            ),
            "scheduler": AgentDefinition(
                description="Schedules approved content for publication on social media platforms.",
                prompt=load_prompt("scheduler"),
                tools=[
                    "mcp__content-engine__read_agent_output",
                    "mcp__content-engine__save_agent_output",
                    "mcp__content-engine__get_platform_specs",
                    "Bash",
                ],
                model="sonnet",
            ),
            "engagement-analyst": AgentDefinition(
                description="Analyzes post-publication engagement metrics and generates insights.",
                prompt=load_prompt("engagement_analyst"),
                tools=[
                    "mcp__content-engine__read_agent_output",
                    "mcp__content-engine__save_agent_output",
                    "Bash",
                ],
                model="sonnet",
            ),
        }

    async def run(self, instruction: str | None = None) -> None:
        """Ejecuta el pipeline completo."""
        self.logger.info("Starting Content Engine Pipeline")

        prompt = instruction or self._build_default_prompt()
        tools_server = create_content_engine_tools()
        subagents = self.get_subagent_definitions()

        options = ClaudeAgentOptions(
            allowed_tools=[
                "Task",
                "Read",
                "Write",
                "Glob",
                "Grep",
                "mcp__content-engine__get_pipeline_state",
                "mcp__content-engine__update_pipeline_state",
                "mcp__content-engine__request_human_approval",
                "mcp__content-engine__read_agent_output",
                "mcp__content-engine__get_brand_guidelines",
            ],
            mcp_servers={"content-engine": tools_server},
            agents=subagents,
        )

        async for message in query(prompt=prompt, options=options):
            if hasattr(message, "content"):
                self.logger.info(f"Orchestrator: {str(message.content)[:200]}")

        self.logger.info("Pipeline execution completed")

    def _build_default_prompt(self) -> str:
        """Construye el prompt por defecto para el orchestrator."""
        system_prompt = self.load_prompt()
        return f"""{system_prompt}

## Tu tarea ahora

Ejecuta el pipeline completo de generación de contenido para A&J Phygital Group.

### Flujo a seguir:
1. **FASE 1 - INVESTIGACIÓN** (paralelo):
   - Usa el agente `trend-researcher` para investigar tendencias actuales
   - Usa el agente `viral-analyzer` para analizar contenido viral del momento

2. **FASE 2 - PLANIFICACIÓN**:
   - Usa el agente `content-planner` para crear el plan de contenido semanal
   - PAUSA: Solicita aprobación humana con `request_human_approval`

3. **FASE 3 - CREACIÓN** (paralelo):
   - Usa el agente `copywriter` para escribir todos los guiones
   - Usa el agente `seo-specialist` para optimizar SEO y hashtags

4. **FASE 4 - PRODUCCIÓN VISUAL** (paralelo):
   - Usa el agente `visual-designer` para generar imágenes
   - Usa el agente `carousel-creator` para crear carruseles
   - (Opcional) Usa `avatar-video-producer` si hay videos con avatar

5. **FASE 5 - VALIDACIÓN**:
   - Usa el agente `brand-guardian` para validar todo el contenido
   - PAUSA: Solicita aprobación humana

6. **FASE 6 - PUBLICACIÓN**:
   - Usa el agente `scheduler` para programar publicaciones
   - PAUSA: Solicita aprobación final antes de publicar

7. **FASE 7 - ANÁLISIS** (post-publicación):
   - Usa el agente `engagement-analyst` para analizar métricas

### Reglas:
- Actualiza el pipeline state después de cada fase con `update_pipeline_state`
- En cada CHECKPOINT, usa `request_human_approval` y DETENTE
- Si un agente falla, registra el error y continúa con los demás
- Target: 3-6 posts/día en Instagram, TikTok, LinkedIn, YouTube, Facebook
- Idiomas: Español + Inglés
"""


async def main():
    """Entry point para ejecutar el Orchestrator."""
    agent = OrchestratorAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
