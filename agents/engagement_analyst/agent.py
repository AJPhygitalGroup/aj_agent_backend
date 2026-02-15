"""
Engagement Analyst Agent - Analiza métricas post-publicación.
"""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, query

from agents.base import BaseAgent
from agents.tools import create_content_engine_tools


class EngagementAnalystAgent(BaseAgent):
    name = "engagement_analyst"
    description = "Analiza métricas de engagement y genera insights accionables"

    async def run(self) -> None:
        self.logger.info("Starting engagement analysis")

        prompt = self.load_prompt()
        tools_server = create_content_engine_tools()

        analysis_prompt = f"""{prompt}

## Ejecución

1. Lee el schedule report: `read_agent_output` con agent_name="scheduler"
2. Lee el content plan original: `read_agent_output` con agent_name="content_planner"

3. Para cada publicación del período:
   a. Recopilar métricas (views, likes, comments, shares, saves, reach, impressions)
   b. Calcular engagement rate por post
   c. Calcular métricas agregadas por plataforma

4. Análisis:
   - Identificar top 5 performers y bottom 5
   - ¿Qué pilar de contenido genera más engagement?
   - ¿Qué formato funciona mejor por plataforma?
   - ¿Qué horarios generan más alcance?
   - ¿Qué tipo de hook retiene más?
   - ¿Qué idioma (ES/EN) performa mejor por plataforma?

5. Generar insights accionables:
   - Recomendaciones para el próximo ciclo
   - Qué temas repetir o evitar
   - Ajustes de horarios sugeridos
   - Formatos a priorizar

6. Feedback loop - datos para retroalimentar:
   - Al Trend Researcher: qué temas funcionan
   - Al Content Planner: ajustar distribución
   - Al Copywriter: qué hooks/CTAs son más efectivos

7. Guarda usando `save_agent_output` con agent_name="engagement_analyst" y suffix="engagement_report"

### Nota:
Si las APIs de analytics no están configuradas aún, genera un template del reporte
con la estructura correcta y métricas placeholder, para que sirva como referencia
cuando las APIs estén activas.
"""

        options = ClaudeAgentOptions(
            allowed_tools=[
                "mcp__content-engine__read_agent_output",
                "mcp__content-engine__save_agent_output",
                "mcp__content-engine__get_brand_guidelines",
            ],
            mcp_servers={"content-engine": tools_server},
        )

        async for message in query(prompt=analysis_prompt, options=options):
            if hasattr(message, "content"):
                self.logger.info(f"EngagementAnalyst: {str(message.content)[:200]}")

        self.logger.info("Engagement analysis completed")


async def main():
    agent = EngagementAnalystAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
