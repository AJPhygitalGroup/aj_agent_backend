"""
Copywriter Agent - Escribe guiones y textos para cada pieza de contenido.
"""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, query

from agents.base import BaseAgent
from agents.tools import create_content_engine_tools


class CopywriterAgent(BaseAgent):
    name = "copywriter"
    description = "Escribe guiones para podcast, reels, TikTok, YouTube, LinkedIn y descripciones"

    async def run(self) -> None:
        self.logger.info("Starting copywriting")

        prompt = self.load_prompt()
        tools_server = create_content_engine_tools()

        copywriting_prompt = f"""{prompt}

## Ejecución

1. Lee el ContentPlan aprobado usando `read_agent_output` con agent_name="content_planner"
2. Lee las brand guidelines usando `get_brand_guidelines`

3. Para CADA pieza del plan, escribe:

   **Reels Instagram (15-60 seg):**
   - Hook (3 seg) + Desarrollo (20-40 seg) + CTA (5 seg)
   - Caption con emojis y estructura
   - ~100-150 palabras

   **Videos TikTok (15-60 seg):**
   - Hook directo (2 seg) + Contenido rápido + CTA breve
   - Caption corto
   - ~80-100 palabras

   **Posts LinkedIn (~200-300 palabras):**
   - Primera línea poderosa (hook pre-"ver más")
   - Desarrollo profesional con datos
   - Pregunta que genere conversación

   **Videos YouTube (8-15 min):**
   - Hook (30 seg) + Intro + Contenido por secciones + Recap + CTA
   - Descripción SEO con timestamps
   - ~1500-2000 palabras

   **Carruseles (5-10 slides):**
   - Cover con hook + slides de contenido + CTA final
   - ~50 palabras por slide

   **Podcast clips:**
   - Intro + Segmentos + Outro + Key takeaways

4. Incluye notas para el Visual Designer y Avatar Video Producer cuando aplique

5. Guarda usando `save_agent_output` con agent_name="copywriter" y suffix="content_scripts"

### Reglas:
- Tono: {self.brand.get('brand', {}).get('voice', {}).get('tone', 'profesional pero accesible')}
- Framework: Hook → Problema → Solución → Prueba → CTA
- NUNCA ser genérico. Cada guión debe aportar valor específico
- Adaptar tono por plataforma (TikTok casual, LinkedIn profesional)
"""

        options = ClaudeAgentOptions(
            allowed_tools=[
                "mcp__content-engine__read_agent_output",
                "mcp__content-engine__save_agent_output",
                "mcp__content-engine__get_brand_guidelines",
            ],
            mcp_servers={"content-engine": tools_server},
        )

        async for message in query(prompt=copywriting_prompt, options=options):
            if hasattr(message, "content"):
                self.logger.info(f"Copywriter: {str(message.content)[:200]}")

        self.logger.info("Copywriting completed")


async def main():
    agent = CopywriterAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
