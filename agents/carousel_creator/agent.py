"""
Carousel Creator Agent - Crea carruseles para Instagram y LinkedIn.
Usa Anthropic API directamente con tool_use.
"""

import json
import os

import httpx

from agents.base import BaseAgent
from utils.api_clients import get_flux_headers
from utils.helpers import get_project_root


class CarouselCreatorAgent(BaseAgent):
    name = "carousel_creator"
    description = "Crea carruseles visuales para Instagram y LinkedIn"
    max_turns = 25

    def get_tools(self) -> list[dict]:
        """Agrega tool de generación de imágenes para slides."""
        tools = self._common_tools()
        tools.append({
            "name": "generate_carousel_slide",
            "description": "Generate a single carousel slide image using Flux API.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Detailed image prompt for the slide"},
                    "slide_number": {"type": "integer", "description": "Slide number (1-based)"},
                    "total_slides": {"type": "integer", "description": "Total number of slides"},
                    "width": {"type": "integer", "description": "Width in pixels (default 1080)"},
                    "height": {"type": "integer", "description": "Height in pixels (default 1080)"},
                    "filename": {"type": "string", "description": "Output filename"},
                },
                "required": ["prompt", "slide_number", "filename"],
            },
        })
        return tools

    def handle_custom_tool(self, tool_name: str, tool_input: dict) -> str:
        if tool_name == "generate_carousel_slide":
            return self._generate_slide(tool_input)
        return f"Unknown tool: {tool_name}"

    def _generate_slide(self, args: dict) -> str:
        """Genera un slide de carrusel con Flux API."""
        headers = get_flux_headers()
        flux_url = os.getenv("FLUX_API_URL", "https://api.flux.ai/v1")

        if not headers.get("Authorization") or "xxxxx" in headers.get("Authorization", ""):
            return (
                f"[Flux API not configured] Would generate slide {args['slide_number']}:\n"
                f"Prompt: {args['prompt'][:200]}\n"
                f"File: {args['filename']}\n"
                f"Configure FLUX_API_KEY in .env to enable."
            )

        output_dir = get_project_root() / "data" / "outputs" / "carousels"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / args["filename"]

        try:
            response = httpx.post(
                f"{flux_url}/images/generations",
                headers=headers,
                json={
                    "prompt": args["prompt"],
                    "width": args.get("width", 1080),
                    "height": args.get("height", 1080),
                },
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()

            if "data" in result and result["data"] and "url" in result["data"][0]:
                img_url = result["data"][0]["url"]
                img_response = httpx.get(img_url, timeout=60)
                output_path.write_bytes(img_response.content)
                return f"Slide {args['slide_number']} saved to: {output_path}"

            return f"Flux API response: {json.dumps(result)[:500]}"
        except Exception as e:
            self.logger.error(f"Flux error: {e}")
            return f"Error generating slide: {str(e)}"

    def _build_prompt(self) -> str:
        return """Crea carruseles visuales para Instagram y LinkedIn de A&J Phygital Group.

## Tu tarea:
1. Usa `read_agent_output` con agent_name="copywriter" para leer los ContentScripts
2. Usa `get_brand_guidelines` para leer las brand guidelines

3. Para cada pieza tipo "carousel" en el plan:
   a. Lee el script del carrusel
   b. Diseña cada slide:
      - Slide 1: Cover con hook visual + título impactante
      - Slides 2 a N-1: Un punto clave por slide, headline + texto corto
      - Slide final: CTA claro + logo de marca
   c. Genera cada slide con `generate_carousel_slide`

4. Formatos:
   - Instagram: 1080x1080 (cuadrado)
   - LinkedIn: 1080x1080 (cuadrado)

5. Brand guidelines para cada slide:
   - Colores: #667eea (azul), #764ba2 (morado), #f093fb (rosa acento)
   - Font: Inter
   - Logo en slide 1 y slide final
   - Estilo: gradientes sutiles, moderno, limpio

6. Nomenclatura: {slot_id}_carousel_slide_{n}.png

7. Guarda resumen usando `save_agent_output` con suffix="carousels_report":
   {
     "carousels": [
       {
         "slot_id": "...",
         "platform": "instagram",
         "total_slides": 7,
         "slides": [{"slide_number": 1, "filename": "...", "status": "success"}]
       }
     ],
     "total_carousels": 4,
     "total_slides_generated": 28
   }"""


def main():
    agent = CarouselCreatorAgent()
    result = agent.run()
    print(result)


if __name__ == "__main__":
    main()
