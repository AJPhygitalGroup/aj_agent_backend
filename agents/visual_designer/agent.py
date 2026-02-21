"""
Visual Designer Agent - Genera imagenes para hooks, thumbnails y posts.
Usa Replicate API (Flux model) para generacion de imagenes de fondo,
y Pillow para agregar texto perfecto con la fuente correcta.
"""

import os

import httpx
import replicate

from agents.base import BaseAgent
from utils.helpers import get_project_root


class VisualDesignerAgent(BaseAgent):
    name = "visual_designer"
    description = "Genera imagenes de hooks, thumbnails y posts con Replicate (Flux) + text overlay con Pillow"
    max_turns = 15

    def get_tools(self) -> list[dict]:
        """Agrega tools de generacion de imagenes y text overlay."""
        tools = self._common_tools()
        tools.append({
            "name": "generate_image",
            "description": (
                "Generate a background image using Flux via Replicate. "
                "IMPORTANT: Do NOT include any text/words/letters in the prompt. "
                "Flux cannot render text correctly. Only describe the visual scene, "
                "colors, style, and composition. Text will be added separately."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": (
                            "Image prompt in ENGLISH. Describe ONLY the visual scene "
                            "(background, colors, objects, style, mood). "
                            "NEVER include text, words, letters, or typography in this prompt."
                        ),
                    },
                    "width": {"type": "integer", "description": "Image width in pixels (default 1080)"},
                    "height": {"type": "integer", "description": "Image height in pixels (default 1080)"},
                    "filename": {"type": "string", "description": "Output filename (e.g. hook_ig_001.png)"},
                },
                "required": ["prompt", "filename"],
            },
        })
        tools.append({
            "name": "add_text_to_image",
            "description": (
                "Add text overlay to a generated image using Pillow. "
                "This renders perfect, crisp text with the Inter font in the correct language. "
                "Use this AFTER generate_image to add hooks, titles, CTAs, etc."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The image filename to add text to (must exist in data/outputs/images/)",
                    },
                    "texts": {
                        "type": "array",
                        "description": "Array of text overlays to add",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "The text to render (in the content's language)"},
                                "position": {
                                    "type": "string",
                                    "description": "Position: 'top', 'center', or 'bottom'",
                                },
                                "font_size": {"type": "integer", "description": "Font size in pixels (default 48)"},
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
                "Use an uploaded brand template as the base image instead of generating with Flux. "
                "Copies the template to the output directory with the desired filename and dimensions. "
                "Use list_templates first to see available templates."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "template_filename": {"type": "string", "description": "Template filename from list_templates"},
                    "output_filename": {"type": "string", "description": "Output filename for this content piece"},
                    "width": {"type": "integer", "description": "Desired width (template will be resized)"},
                    "height": {"type": "integer", "description": "Desired height (template will be resized)"},
                },
                "required": ["template_filename", "output_filename"],
            },
        })
        return tools

    def handle_custom_tool(self, tool_name: str, tool_input: dict) -> str:
        if tool_name == "generate_image":
            return self._generate_image(tool_input)
        elif tool_name == "add_text_to_image":
            return self._add_text_overlay(tool_input)
        elif tool_name == "use_template":
            return self._use_template(tool_input, "images")
        return f"Unknown tool: {tool_name}"

    def _generate_image(self, args: dict) -> str:
        """Genera una imagen de fondo usando Flux via Replicate (sin texto)."""
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

            img_url = str(output)
            img_response = httpx.get(img_url, timeout=60)
            img_response.raise_for_status()
            output_path.write_bytes(img_response.content)
            self.logger.info(f"Image saved: {output_path}")
            return f"Image saved to: {output_path}. Now use add_text_to_image to add any text overlays."

        except Exception as e:
            self.logger.error(f"Replicate error: {e}")
            return f"Error generating image: {str(e)}"

    def _add_text_overlay(self, args: dict) -> str:
        """Agrega texto perfecto sobre la imagen usando Pillow."""
        try:
            from utils.image_text import add_text_overlay

            images_dir = get_project_root() / "data" / "outputs" / "images"
            image_path = images_dir / args["filename"]

            if not image_path.exists():
                return f"Error: Image not found at {image_path}"

            texts = args.get("texts", [])
            if not texts:
                return "No texts provided"

            add_text_overlay(image_path, texts)
            return f"Text overlay added to {args['filename']} successfully."

        except Exception as e:
            self.logger.error(f"Text overlay error: {e}")
            return f"Error adding text: {str(e)}"

    def _use_template(self, args: dict, output_subdir: str) -> str:
        """Copy and resize a template to use as base image."""
        try:
            from PIL import Image

            templates_dir = get_project_root() / "data" / "inputs" / "templates"
            template_path = templates_dir / args["template_filename"]

            if not template_path.exists():
                return f"Error: Template not found: {args['template_filename']}"

            output_dir = get_project_root() / "data" / "outputs" / output_subdir
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / args["output_filename"]

            img = Image.open(template_path)
            w = args.get("width", img.width)
            h = args.get("height", img.height)
            if (w, h) != (img.width, img.height):
                img = img.resize((w, h), Image.LANCZOS)
            img.save(str(output_path), "PNG", quality=95)

            return f"Template applied: {output_path}. Now use add_text_to_image to add text overlays."

        except Exception as e:
            self.logger.error(f"Template error: {e}")
            return f"Error using template: {str(e)}"

    def _build_prompt(self) -> str:
        return """Genera imagenes para todo el contenido visual de A&J Phygital Group.

## REGLA CRITICA: SEPARAR IMAGEN Y TEXTO
Flux (el modelo de IA que genera imagenes) NO puede renderizar texto correctamente.
Siempre genera errores ortograficos cuando intentas poner texto en las imagenes.

**PROCESO OBLIGATORIO para cada imagen:**
1. Usa `generate_image` para crear la IMAGEN DE FONDO solamente
   - El prompt debe ser SOLO en INGLES
   - NUNCA incluyas texto, palabras, letras o tipografia en el prompt
   - Describe solo: escena visual, colores, estilo, composicion, mood
2. Usa `add_text_to_image` para agregar el texto
   - El texto debe estar en el IDIOMA DEL CONTENIDO (español o inglés segun el slot)
   - Verifica ortografia antes de enviarlo
   - Usa posicion "top" para hooks, "center" para titulos, "bottom" para CTAs

## Tu tarea:
1. Usa `read_agent_output` con agent_name="copywriter" para leer los ContentScripts
2. Usa `get_brand_guidelines` para leer las brand guidelines
3. Usa `list_templates` para ver si hay plantillas de marca subidas

4. Para cada pieza de contenido que requiera imagenes:
   - **SI hay templates disponibles:** usa `use_template` para copiar la plantilla como base
   - **SI NO hay templates:** usa `generate_image` para generar fondo con Flux

5. Para cada pieza de contenido que requiera imagenes:
   a. Identifica el idioma del contenido (slot.language: "es" o "en")
   b. Crea un prompt de IMAGEN DE FONDO en INGLES para Flux:
      - Colores de marca: azul (#667eea), morado (#764ba2)
      - Estilo: profesional, moderno, tecnologico, gradientes sutiles
      - NO incluir texto, palabras, ni letras en el prompt
      - Solo describir escena visual, composicion, colores
   c. Genera la imagen con `generate_image`
   d. Agrega texto con `add_text_to_image`:
      - Hook text en la posicion "top" o "center" (font_size: 56-72)
      - CTA en posicion "bottom" si aplica (font_size: 32-40)
      - Color blanco (#FFFFFF) para fondos oscuros, oscuro (#1a1a2e) para fondos claros

4. Tipos de imagenes a generar:
   - Thumbnails YouTube: 1280x720
   - Hook images reels/TikTok: 1080x1920
   - Post images Instagram: 1080x1080
   - Post images Facebook: 1200x630
   - Post images LinkedIn: 1200x627

5. Nomenclatura: {slot_id}_{tipo}_{variante}.png

## Ejemplo de prompt CORRECTO para generate_image:
"Professional modern tech background with deep blue (#667eea) to purple (#764ba2) gradient,
abstract geometric shapes, subtle bokeh lights, clean minimalist composition,
corporate tech aesthetic, dark overlay area at top for text placement"

## Ejemplo de prompt INCORRECTO (NUNCA hacer esto):
"Image with text saying 'Automate your business' in bold letters"

6. Guarda un resumen usando `save_agent_output` con suffix="images_report":
   {
     "images_generated": [
       {"slot_id": "...", "filename": "...", "type": "thumbnail", "dimensions": "1280x720", "status": "success", "text_added": true}
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
