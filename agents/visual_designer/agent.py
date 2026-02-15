"""
Visual Designer Agent - Genera imágenes para hooks, thumbnails y posts.
Usa Anthropic API directamente con tool_use.
"""

import json
import os

import httpx

from agents.base import BaseAgent
from utils.api_clients import get_flux_headers
from utils.helpers import get_project_root


class VisualDesignerAgent(BaseAgent):
    name = "visual_designer"
    description = "Genera imágenes de hooks, thumbnails y posts con Flux API"
    max_turns = 25

    def get_tools(self) -> list[dict]:
        """Agrega tool de generación de imágenes con Flux."""
        tools = self._common_tools()
        tools.append({
            "name": "generate_image_flux",
            "description": "Generate an image using the Flux API. Provide a detailed prompt describing the image.",
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
        if tool_name == "generate_image_flux":
            return self._generate_image(tool_input)
        return f"Unknown tool: {tool_name}"

    def _generate_image(self, args: dict) -> str:
        """Llama a la Flux API para generar una imagen."""
        headers = get_flux_headers()
        flux_url = os.getenv("FLUX_API_URL", "https://api.flux.ai/v1")

        if not headers.get("Authorization") or "xxxxx" in headers.get("Authorization", ""):
            return (
                f"[Flux API not configured] Would generate image:\n"
                f"Prompt: {args['prompt'][:200]}\n"
                f"Size: {args.get('width', 1080)}x{args.get('height', 1080)}\n"
                f"File: {args['filename']}\n"
                f"Configure FLUX_API_KEY in .env to enable image generation."
            )

        payload = {
            "prompt": args["prompt"],
            "width": args.get("width", 1080),
            "height": args.get("height", 1080),
        }

        output_dir = get_project_root() / "data" / "outputs" / "images"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / args["filename"]

        try:
            response = httpx.post(
                f"{flux_url}/images/generations",
                headers=headers,
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()

            if "data" in result and result["data"] and "url" in result["data"][0]:
                img_url = result["data"][0]["url"]
                img_response = httpx.get(img_url, timeout=60)
                output_path.write_bytes(img_response.content)
                return f"Image saved to: {output_path}"

            return f"Flux API response: {json.dumps(result)[:500]}"
        except Exception as e:
            self.logger.error(f"Flux error: {e}")
            return f"Error generating image: {str(e)}. Make sure FLUX_API_KEY is set in .env"

    def _build_prompt(self) -> str:
        return """Genera imágenes para todo el contenido visual de A&J Phygital Group.

## Tu tarea:
1. Usa `read_agent_output` con agent_name="copywriter" para leer los ContentScripts
2. Usa `get_brand_guidelines` para leer las brand guidelines

3. Para cada pieza de contenido que requiera imágenes:
   a. Analiza el hook y tema del guión
   b. Crea un prompt detallado en INGLÉS para Flux API basado en:
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
