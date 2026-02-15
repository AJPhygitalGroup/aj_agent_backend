"""
Viral Analyzer Agent - Analiza la estructura de contenido viral.
"""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, query

from agents.base import BaseAgent
from agents.tools import create_content_engine_tools


class ViralAnalyzerAgent(BaseAgent):
    name = "viral_analyzer"
    description = "Analiza estructura, tono, música y guión de contenido viral"

    async def run(self) -> None:
        self.logger.info("Starting viral content analysis")

        prompt = self.load_prompt()
        tools_server = create_content_engine_tools()

        analysis_prompt = f"""{prompt}

## Ejecución

1. Lee el TrendReport del trend_researcher usando `read_agent_output`
2. Busca y analiza los videos/posts más virales del momento en el nicho de IA, SaaS y automatización
3. Para cada contenido viral, analiza:
   - Hook/gancho (tipo, texto, duración)
   - Tono (educativo, entretenido, inspiracional, etc.)
   - Música/audio (trending, original, none)
   - Estructura del guión (hook → desarrollo → CTA)
   - Tipo de video (talking head, screen recording, etc.)
   - Métricas (views, likes, engagement)
4. Detecta patrones comunes entre los contenidos más exitosos
5. Genera recomendaciones de formato por plataforma

### Output:
Genera un ViralAnalysisReport con:
- Mínimo 10 contenidos virales analizados
- Patrones detectados
- Top hooks recomendados
- Formatos ganadores por plataforma

Guarda usando `save_agent_output` con agent_name="viral_analyzer" y suffix="viral_analysis".
"""

        options = ClaudeAgentOptions(
            allowed_tools=[
                "WebSearch",
                "WebFetch",
                "mcp__content-engine__read_agent_output",
                "mcp__content-engine__save_agent_output",
                "mcp__content-engine__get_brand_guidelines",
            ],
            mcp_servers={"content-engine": tools_server},
        )

        async for message in query(prompt=analysis_prompt, options=options):
            if hasattr(message, "content"):
                self.logger.info(f"ViralAnalyzer: {str(message.content)[:200]}")

        self.logger.info("Viral analysis completed")


async def main():
    agent = ViralAnalyzerAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
