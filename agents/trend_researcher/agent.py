"""
Trend Researcher Agent - Investiga tendencias en redes sociales y Google.
"""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, query

from agents.base import BaseAgent
from agents.tools import create_content_engine_tools


class TrendResearcherAgent(BaseAgent):
    name = "trend_researcher"
    description = "Investiga tendencias en redes sociales y Google"

    async def run(self) -> None:
        self.logger.info("Starting trend research")

        prompt = self.load_prompt()
        tools_server = create_content_engine_tools()

        research_prompt = f"""{prompt}

## Ejecución

Investiga las tendencias actuales en estas plataformas:
1. Google Trends - tendencias de búsqueda
2. Instagram - reels trending, hashtags populares
3. TikTok - videos virales, sonidos trending
4. LinkedIn - temas profesionales en tendencia
5. YouTube - videos trending en el nicho
6. Facebook - temas trending

### Nicho a investigar:
- Automatización de procesos con IA
- Chatbots de WhatsApp
- Aplicaciones SaaS
- E-commerce consulting
- Transformación digital para SMBs

### Idiomas: Español + Inglés

### Output:
Genera un TrendReport completo con:
- Tendencias por plataforma (mínimo 5 por plataforma)
- Top 10 tendencias globales combinadas
- Temas recomendados para crear contenido
- Score de relevancia (0-1) para cada tendencia

Guarda el resultado usando `save_agent_output` con agent_name="trend_researcher" y suffix="trend_report".
"""

        options = ClaudeAgentOptions(
            allowed_tools=[
                "WebSearch",
                "WebFetch",
                "mcp__content-engine__save_agent_output",
                "mcp__content-engine__get_brand_guidelines",
            ],
            mcp_servers={"content-engine": tools_server},
        )

        async for message in query(prompt=research_prompt, options=options):
            if hasattr(message, "content"):
                self.logger.info(f"TrendResearcher: {str(message.content)[:200]}")

        self.logger.info("Trend research completed")


async def main():
    agent = TrendResearcherAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
