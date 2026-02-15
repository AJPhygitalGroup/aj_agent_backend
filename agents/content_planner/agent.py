"""
Content Planner Agent - Genera el plan de contenido semanal.
"""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, query

from agents.base import BaseAgent
from agents.tools import create_content_engine_tools


class ContentPlannerAgent(BaseAgent):
    name = "content_planner"
    description = "Genera plan de contenido semanal y lo exporta a Google Sheets"

    async def run(self) -> None:
        self.logger.info("Starting content planning")

        prompt = self.load_prompt()
        tools_server = create_content_engine_tools()

        planning_prompt = f"""{prompt}

## Ejecución

1. Lee el TrendReport del trend_researcher usando `read_agent_output` con agent_name="trend_researcher"
2. Lee el ViralAnalysisReport del viral_analyzer usando `read_agent_output` con agent_name="viral_analyzer"
3. Lee las brand guidelines usando `get_brand_guidelines`
4. Lee las specs de plataformas usando `get_platform_specs`

5. Crea un plan de contenido para los próximos 7 días con:
   - 3-6 posts por día
   - Distribución: Instagram (2/día), TikTok (2/día), LinkedIn (1/día), Facebook (1/día), YouTube (3-4/semana)
   - Respetar los pilares de contenido:
     * 30% AI Automations & Chatbots
     * 25% SaaS & App Development
     * 20% E-commerce Consulting
     * 15% Thought Leadership
     * 10% Educación y Valor

6. Para cada pieza de contenido define:
   - Fecha y hora de publicación
   - Plataforma y tipo de contenido (reel, carousel, post, video, etc.)
   - Tema y ángulo específico
   - Idea de hook/gancho
   - Patrón viral a aplicar (del ViralAnalysisReport)
   - Idioma (ES o EN)
   - Pilar de contenido
   - Prioridad (high/medium/low)

7. Guarda el plan usando `save_agent_output` con agent_name="content_planner" y suffix="content_plan"

### Reglas:
- NO repetir el mismo tema en el mismo día en diferentes plataformas
- Adaptar el ángulo a cada plataforma
- Alternar entre pilares para mantener variedad
- Incluir al menos 1 contenido educativo de alto valor por día
- Priorizar temas con tendencias rising
"""

        options = ClaudeAgentOptions(
            allowed_tools=[
                "mcp__content-engine__read_agent_output",
                "mcp__content-engine__save_agent_output",
                "mcp__content-engine__get_brand_guidelines",
                "mcp__content-engine__get_platform_specs",
            ],
            mcp_servers={"content-engine": tools_server},
        )

        async for message in query(prompt=planning_prompt, options=options):
            if hasattr(message, "content"):
                self.logger.info(f"ContentPlanner: {str(message.content)[:200]}")

        self.logger.info("Content planning completed")


async def main():
    agent = ContentPlannerAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
