"""
SEO & Hashtag Specialist Agent - Optimiza SEO, hashtags y keywords.
"""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, query

from agents.base import BaseAgent
from agents.tools import create_content_engine_tools


class SEOHashtagSpecialistAgent(BaseAgent):
    name = "seo_hashtag_specialist"
    description = "Optimiza SEO, hashtags y keywords para máximo alcance orgánico"

    async def run(self) -> None:
        self.logger.info("Starting SEO & hashtag optimization")

        prompt = self.load_prompt()
        tools_server = create_content_engine_tools()

        seo_prompt = f"""{prompt}

## Ejecución

1. Lee los ContentScripts del copywriter usando `read_agent_output` con agent_name="copywriter"
2. Lee las brand guidelines usando `get_brand_guidelines`

3. Para CADA pieza de contenido:
   a. Investiga hashtags trending del momento para la plataforma + nicho
   b. Genera set de hashtags (3 niveles):
      - Primarios (alto volumen, 500K+ posts)
      - Secundarios (nicho medio, 50K-500K)
      - Long-tail (específicos, <50K)
   c. Incluye hashtags de marca: #AJPhygitalGroup, #AutomateGrowDominate
   d. Optimiza título para SEO
   e. Optimiza descripción con keywords naturales
   f. Genera alt text para imágenes
   g. Para YouTube: genera tags y keywords research

4. Cantidades por plataforma:
   - Instagram: hasta 25 hashtags
   - TikTok: 3-5 hashtags
   - LinkedIn: 3-5 hashtags
   - YouTube: 10-15 tags
   - Facebook: 3-5 hashtags

5. Identifica keyword opportunities (alto volumen, baja competencia)

6. Guarda usando `save_agent_output` con agent_name="seo_hashtag_specialist" y suffix="seo_optimizations"

### Reglas:
- NO usar hashtags baneados o shadowbanned
- NO repetir exactamente el mismo set de hashtags en posts consecutivos
- Priorizar hashtags en el idioma del contenido
"""

        options = ClaudeAgentOptions(
            allowed_tools=[
                "WebSearch",
                "mcp__content-engine__read_agent_output",
                "mcp__content-engine__save_agent_output",
                "mcp__content-engine__get_brand_guidelines",
            ],
            mcp_servers={"content-engine": tools_server},
        )

        async for message in query(prompt=seo_prompt, options=options):
            if hasattr(message, "content"):
                self.logger.info(f"SEOSpecialist: {str(message.content)[:200]}")

        self.logger.info("SEO optimization completed")


async def main():
    agent = SEOHashtagSpecialistAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
