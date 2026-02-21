"""
Carousel Creator Agent - Crea carruseles para Instagram y LinkedIn.
Usa Replicate API (Flux model) para imagenes de fondo,
y Pillow para agregar texto perfecto con la fuente correcta.
"""

import os

import httpx
import replicate

from agents.base import BaseAgent
from utils.helpers import get_project_root


class CarouselCreatorAgent(BaseAgent):
    name = "carousel_creator"
    description = "Crea carruseles visuales para Instagram y LinkedIn"
    max_turns = 15

    def get_tools(self) -> list[dict]:
        """Agrega tools de generacion de slides y text overlay."""
        tools = self._common_tools()
        tools.append({
            "name": "generate_carousel_slide",
            "description": (
                "Generate a carousel slide BACKGROUND image using Flux via Replicate. "
                "IMPORTANT: Do NOT include any text/words/letters in the prompt. "
                "Flux cannot render text correctly. Only describe visual elements. "
                "Text will be added separately with add_text_to_slide."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": (
                            "Image prompt in ENGLISH. Describe ONLY the visual background "
                            "(colors, gradients, shapes, style). "
                            "NEVER include text, words, letters, or numbers in this prompt."
                        ),
                    },
                    "slide_number": {"type": "integer", "description": "Slide number (1-based)"},
                    "total_slides": {"type": "integer", "description": "Total number of slides"},
                    "width": {"type": "integer", "description": "Width in pixels (default 1080)"},
                    "height": {"type": "integer", "description": "Height in pixels (default 1080)"},
                    "filename": {"type": "string", "description": "Output filename"},
                },
                "required": ["prompt", "slide_number", "filename"],
            },
        })
        tools.append({
            "name": "add_text_to_slide",
            "description": (
                "Add text overlay to a carousel slide using Pillow. "
                "Renders perfect, crisp text in the correct language with Inter font. "
                "Use this AFTER generate_carousel_slide to add titles, bullet points, CTAs."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The slide filename to add text to (must exist in data/outputs/carousels/)",
                    },
                    "texts": {
                        "type": "array",
                        "description": "Array of text overlays to add to the slide",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "The text to render"},
                                "position": {
                                    "type": "string",
                                    "description": "Position: 'top', 'center', or 'bottom'",
                                },
                                "font_size": {"type": "integer", "description": "Font size (default 48)"},
                                "color": {"type": "string", "description": "Text color hex (default #FFFFFF)"},
                                "shadow": {"type": "boolean", "description": "Add drop shadow (default true)"},
                            },
                            "required": ["text", "position"],
                        },
                    },
                },
                "required": ["filename", "texts"],
            },
        })
        tools.append({
            "name": "use_template",
            "description": (
                "Use an uploaded brand template as the base slide instead of generating with Flux. "
                "Copies the template to the carousels output with the desired dimensions. "
                "Use list_templates first to see available templates."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "template_filename": {"type": "string", "description": "Template filename from list_templates"},
                    "output_filename": {"type": "string", "description": "Output filename for this slide"},
                    "width": {"type": "integer", "description": "Desired width (template will be resized)"},
                    "height": {"type": "integer", "description": "Desired height (template will be resized)"},
                },
                "required": ["template_filename", "output_filename"],
            },
        })
        return tools

    def handle_custom_tool(self, tool_name: str, tool_input: dict) -> str:
        if tool_name == "generate_carousel_slide":
            return self._generate_slide(tool_input)
        elif tool_name == "add_text_to_slide":
            return self._add_text_overlay(tool_input)
        elif tool_name == "use_template":
            return self._use_template(tool_input)
        return f"Unknown tool: {tool_name}"

    def _generate_slide(self, args: dict) -> str:
        """Genera un slide de fondo con Flux via Replicate (sin texto)."""
        api_token = os.getenv("REPLICATE_API_TOKEN", "")
        if not api_token or "xxxxx" in api_token:
            return (
                f"[Replicate not configured] Would generate slide {args['slide_number']}:\n"
                f"Prompt: {args['prompt'][:200]}\n"
                f"File: {args['filename']}\n"
                f"Configure REPLICATE_API_TOKEN in .env to enable."
            )

        output_dir = get_project_root() / "data" / "outputs" / "carousels"
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

            img_url = str(output)
            img_response = httpx.get(img_url, timeout=60)
            img_response.raise_for_status()
            output_path.write_bytes(img_response.content)
            self.logger.info(f"Slide saved: {output_path}")
            return f"Slide {args['slide_number']} saved to: {output_path}. Now use add_text_to_slide to add text."

        except Exception as e:
            self.logger.error(f"Replicate error: {e}")
            return f"Error generating slide: {str(e)}"

    def _add_text_overlay(self, args: dict) -> str:
        """Agrega texto perfecto sobre el slide usando Pillow."""
        try:
            from utils.image_text import add_text_overlay

            carousels_dir = get_project_root() / "data" / "outputs" / "carousels"
            image_path = carousels_dir / args["filename"]

            if not image_path.exists():
                return f"Error: Slide not found at {image_path}"

            texts = args.get("texts", [])
            if not texts:
                return "No texts provided"

            add_text_overlay(image_path, texts)
            return f"Text overlay added to {args['filename']} successfully."

        except Exception as e:
            self.logger.error(f"Text overlay error: {e}")
            return f"Error adding text: {str(e)}"

    def _use_template(self, args: dict) -> str:
        """Copy and resize a template to use as base slide."""
        try:
            from PIL import Image

            templates_dir = get_project_root() / "data" / "inputs" / "templates"
            template_path = templates_dir / args["template_filename"]

            if not template_path.exists():
                return f"Error: Template not found: {args['template_filename']}"

            output_dir = get_project_root() / "data" / "outputs" / "carousels"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / args["output_filename"]

            img = Image.open(template_path)
            w = args.get("width", img.width)
            h = args.get("height", img.height)
            if (w, h) != (img.width, img.height):
                img = img.resize((w, h), Image.LANCZOS)
            img.save(str(output_path), "PNG", quality=95)

            return f"Template applied: {output_path}. Now use add_text_to_slide to add text overlays."

        except Exception as e:
            self.logger.error(f"Template error: {e}")
            return f"Error using template: {str(e)}"

    def _build_prompt(self) -> str:
        return """Crea carruseles visuales para Instagram y LinkedIn de A&J Phygital Group.

## REGLA CRITICA: SEPARAR IMAGEN Y TEXTO
Flux (el modelo de IA) NO puede renderizar texto correctamente.
Siempre genera errores ortograficos y mezcla idiomas.

**PROCESO OBLIGATORIO para cada slide:**
1. Usa `generate_carousel_slide` para crear el FONDO VISUAL solamente
   - Prompt en INGLES
   - NUNCA incluir texto, palabras, letras o numeros en el prompt
   - Solo: colores, gradientes, formas, estilo visual
2. Usa `add_text_to_slide` para agregar texto perfecto
   - Texto en el IDIOMA DEL CONTENIDO (español o inglés segun el slot)
   - Verifica ortografia y acentos antes de enviarlo

## Tu tarea:
1. Usa `read_agent_output` con agent_name="copywriter" para leer los ContentScripts
2. Usa `get_brand_guidelines` para leer las brand guidelines
3. Usa `list_templates` para ver si hay plantillas de marca subidas

4. Para cada pieza tipo "carousel" en el plan:
   - **SI hay templates disponibles:** usa `use_template` para cada slide
   - **SI NO hay templates:** usa `generate_carousel_slide` para generar fondos con Flux

5. Para cada pieza tipo "carousel" en el plan:
   a. Lee el script del carrusel e identifica el idioma
   b. Genera el FONDO de cada slide (sin texto):
      - Mantener estilo visual consistente entre todos los slides del mismo carrusel
      - Usar colores de marca: #667eea (azul), #764ba2 (morado), #f093fb (rosa)
      - Fondos con gradientes sutiles, formas geometricas, estilo tech moderno
   c. Agrega texto a cada slide:
      - Slide 1 (Cover): Hook en "center" (font_size: 64), subtitulo en "bottom" (font_size: 36)
      - Slides intermedios: Headline en "top" (font_size: 48), texto en "center" (font_size: 32)
      - Slide final: CTA en "center" (font_size: 52), detalle en "bottom" (font_size: 28)

4. Formatos:
   - Instagram: 1080x1080 (cuadrado)
   - LinkedIn: 1080x1080 (cuadrado)

5. Ejemplo de prompt CORRECTO para generate_carousel_slide:
   "Clean modern slide background with deep blue to purple gradient (#667eea to #764ba2),
   subtle geometric patterns, professional tech aesthetic, large empty center area for text,
   minimalist design with soft lighting effects"

6. Ejemplo INCORRECTO (NUNCA hacer esto):
   "Slide with text saying '5 Ways to Use AI' in bold white letters"

7. Nomenclatura: {slot_id}_carousel_slide_{n}.png

8. Guarda resumen usando `save_agent_output` con suffix="carousels_report":
   {
     "carousels": [
       {
         "slot_id": "...",
         "platform": "instagram",
         "total_slides": 7,
         "slides": [{"slide_number": 1, "filename": "...", "status": "success", "text_added": true}]
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
