"""
Visual Designer Agent - Genera imagenes para hooks, thumbnails y posts.
Usa Replicate API (Flux model) para generacion de imagenes.
"""

import os

import httpx
import replicate

from agents.base import BaseAgent
from utils.helpers import get_project_root


class VisualDesignerAgent(BaseAgent):
    name = "visual_designer"
    description = "Genera imagenes de hooks, thumbnails y posts con Replicate (Flux)"
    max_turns = 15  # Haiku: builds prompts for Flux, doesn't need Sonnet

    def get_tools(self) -> list[dict]:
        """Agrega tool de generacion de imagenes."""
        tools = self._common_tools()
        tools.append({
            "name": "generate_image",
            "description": "Generate an image using Flux via Replicate. Provide a detailed prompt in English.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Detailed image generation prompt in English"},
                    "width": {"type": "integer", "description": "Image width in pixels (default 1080)"},
                    "height": {"type": "integer", "description": "Image height in pixels (default 1080)"},
                    "filename": {"type": "string", "description": "Output filename (e.g. hook_ig_001.png)"},
                },
                "required": ["prompt", "filename"],
            },
        })
        return tools

    def handle_custom_tool(self, tool_name: str, tool_input: dict) -> str:
        if tool_name == "generate_image":
            return self._generate_image(tool_input)
        return f"Unknown tool: {tool_name}"

    def _generate_image(self, args: dict) -> str:
        """Genera una imagen usando Flux via Replicate."""
        api_token = os.getenv("REPLICATE_API_TOKEN", "")
        if not api_token or "xxxxx" in api_token:
            return (
                f"[Replicate not configured] Would generate image:\n"
                f"Prompt: {args['prompt'][:200]}\n"
                f"Size: {args.get('width', 1080)}x{args.get('height', 1080)}\n"
                f"File: {args['filename']}\n"
                f"Configure REPLICATE_API_TOKEN in .env to enable image generation."
            )

        output_dir = get_project_root() / "data" / "outputs" / "images"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / args["filename"]

        try:
            output = replicate.run(
                "black-forest-labs/flux-1.1-pro",
                input={
                    "prompt": args["prompt"],
                    "width": args.get("width", 1080),
                    "height": args.get("height", 1080),
                    "output_format": "png",
                    "prompt_upsampling": True,
                },
            )

            # output is a FileOutput URL - download it
            img_url = str(output)
            img_response = httpx.get(img_url, timeout=60)
            img_response.raise_for_status()
            output_path.write_bytes(img_response.content)
            self.logger.info(f"Image saved: {output_path}")
            return f"Image saved to: {output_path}"

        except Exception as e:
            self.logger.error(f"Replicate error: {e}")
            return f"Error generating image: {str(e)}"

    def _build_prompt(self) -> str:
        return """Genera imagenes para todo el contenido visual de A&J Phygital Group.

## Tu tarea:
1. Usa `read_agent_output` con agent_name="copywriter" para leer los ContentScripts
2. Usa `get_brand_guidelines` para leer las brand guidelines

3. Para cada pieza de contenido que requiera imagenes:
   a. Analiza el hook y tema del guion
   b. Crea un prompt detallado en INGLES para Flux basado en:
      - El mensaje del hook
      - Los colores de marca (#667eea azul, #764ba2 morado)
      - Estilo profesional y moderno
      - Tipografia Inter
   c. Genera la imagen con `generate_image`

4. Tipos de imagenes a generar:
   - Thumbnails YouTube: 1280x720
   - Hook images reels/TikTok: 1080x1920
   - Post images Instagram: 1080x1080
   - Post images Facebook: 1200x630
   - Post images LinkedIn: 1200x627

5. Nomenclatura: {slot_id}_{tipo}_{variante}.png

6. Guarda un resumen usando `save_agent_output` con suffix="images_report":
   {
     "images_generated": [
       {"slot_id": "...", "filename": "...", "type": "thumbnail", "dimensions": "1280x720", "status": "success"}
     ],
     "total_images": 15,
     "failed": []
   }"""


def main():
    agent = VisualDesignerAgent()
    result = agent.run()
    print(result)


if __name__ == "__main__":
    main()
