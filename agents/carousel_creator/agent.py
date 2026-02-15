"""
Carousel Creator Agent - Crea carruseles para Instagram y LinkedIn.
"""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, query

from agents.base import BaseAgent
from agents.tools import create_content_engine_tools
from agents.visual_designer.agent import generate_image_flux


class CarouselCreatorAgent(BaseAgent):
    name = "carousel_creator"
    description = "Crea carruseles visuales para Instagram y LinkedIn"

    async def run(self) -> None:
        self.logger.info("Starting carousel creation")

        prompt = self.load_prompt()
        content_engine_tools = create_content_engine_tools()
        flux_tools = create_sdk_mcp_server(
            name="flux-tools",
            version="1.0.0",
            tools=[generate_image_flux],
        )

        carousel_prompt = f"""{prompt}

## Ejecución

1. Lee los ContentScripts del copywriter usando `read_agent_output` con agent_name="copywriter"
2. Lee las brand guidelines usando `get_brand_guidelines`

3. Para cada pieza tipo "carousel" en el plan:
   a. Lee el CarouselScript correspondiente
   b. Diseña cada slide:
      - Slide 1: Cover con hook visual + título
      - Slides 2 a N-1: Un punto por slide, headline + texto
      - Slide final: CTA + logo de marca
   c. Genera cada slide como imagen con `generate_image_flux`

4. Formatos:
   - Instagram: 1080x1080 (cuadrado)
   - LinkedIn: 1080x1080 (cuadrado, se exporta como PDF)

5. Brand guidelines:
   - Colores: #667eea (azul), #764ba2 (morado), #f093fb (rosa acento)
   - Font: Inter
   - Logo en slide 1 y slide final

6. Nomenclatura: {{content_slot_id}}_carousel_slide_{{n}}.png

7. Guarda resumen usando `save_agent_output` con agent_name="carousel_creator" y suffix="carousels_report"
"""

        options = ClaudeAgentOptions(
            allowed_tools=[
                "mcp__content-engine__read_agent_output",
                "mcp__content-engine__save_agent_output",
                "mcp__content-engine__get_brand_guidelines",
                "mcp__flux-tools__generate_image_flux",
            ],
            mcp_servers={
                "content-engine": content_engine_tools,
                "flux-tools": flux_tools,
            },
        )

        async for message in query(prompt=carousel_prompt, options=options):
            if hasattr(message, "content"):
                self.logger.info(f"CarouselCreator: {str(message.content)[:200]}")

        self.logger.info("Carousel creation completed")


async def main():
    agent = CarouselCreatorAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
