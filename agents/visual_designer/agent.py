"""
Visual Designer Agent - Genera imágenes para hooks, thumbnails y posts.
"""

import asyncio
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, query, tool

from agents.base import BaseAgent
from agents.tools import create_content_engine_tools
from utils.api_clients import get_flux_headers


@tool(
    "generate_image_flux",
    "Generate an image using the Flux API. Provide a detailed prompt describing the image to create.",
    {
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "Detailed image generation prompt"},
            "width": {"type": "integer", "description": "Image width in pixels"},
            "height": {"type": "integer", "description": "Image height in pixels"},
            "filename": {"type": "string", "description": "Output filename (without path)"},
        },
        "required": ["prompt", "filename"],
    },
)
async def generate_image_flux(args: dict[str, Any]) -> dict[str, Any]:
    """Llama a la Flux API para generar una imagen."""
    import httpx
    import os
    from utils.helpers import get_project_root

    headers = get_flux_headers()
    flux_url = os.getenv("FLUX_API_URL", "https://api.flux.ai/v1")

    payload = {
        "prompt": args["prompt"],
        "width": args.get("width", 1080),
        "height": args.get("height", 1080),
    }

    output_dir = get_project_root() / "data" / "outputs" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / args["filename"]

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{flux_url}/images/generations",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            result = response.json()

            # Descargar la imagen si la API devuelve una URL
            if "url" in result.get("data", [{}])[0]:
                img_url = result["data"][0]["url"]
                img_response = await client.get(img_url)
                output_path.write_bytes(img_response.content)
                return {"content": [{"type": "text", "text": f"Image saved to: {output_path}"}]}

            return {"content": [{"type": "text", "text": f"Flux API response: {result}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error generating image: {str(e)}. Make sure FLUX_API_KEY is set in .env"}]}


class VisualDesignerAgent(BaseAgent):
    name = "visual_designer"
    description = "Genera imágenes de hooks, thumbnails y posts con Flux API"

    async def run(self) -> None:
        self.logger.info("Starting visual design")

        prompt = self.load_prompt()
        content_engine_tools = create_content_engine_tools()
        flux_tools = create_sdk_mcp_server(
            name="flux-tools",
            version="1.0.0",
            tools=[generate_image_flux],
        )

        design_prompt = f"""{prompt}

## Ejecución

1. Lee los ContentScripts del copywriter usando `read_agent_output` con agent_name="copywriter"
2. Lee las brand guidelines usando `get_brand_guidelines`

3. Para cada pieza de contenido que requiera imágenes:
   a. Analiza el hook y tema del guión
   b. Crea un prompt detallado para Flux API basado en:
      - El mensaje del hook
      - Los colores de marca (#667eea azul, #764ba2 morado)
      - Estilo profesional y moderno
      - Tipografía Inter
   c. Genera la imagen con `generate_image_flux`

4. Tipos de imágenes a generar:
   - Thumbnails YouTube: 1280x720
   - Hook images reels/TikTok: 1080x1920
   - Post images Instagram: 1080x1080
   - Post images Facebook: 1200x630
   - Post images LinkedIn: 1200x627

5. Nomenclatura: {{content_slot_id}}_{{tipo}}_{{variante}}.png

6. Guarda un resumen usando `save_agent_output` con agent_name="visual_designer" y suffix="images_report"
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

        async for message in query(prompt=design_prompt, options=options):
            if hasattr(message, "content"):
                self.logger.info(f"VisualDesigner: {str(message.content)[:200]}")

        self.logger.info("Visual design completed")


async def main():
    agent = VisualDesignerAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
