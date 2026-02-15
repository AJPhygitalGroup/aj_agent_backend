"""
Avatar Video Producer Agent - Genera videos con avatar de IA via HeyGen.
Usa Anthropic API directamente con tool_use.
Se activa bajo demanda.
"""

import os

import httpx

from agents.base import BaseAgent
from utils.api_clients import get_heygen_headers


class AvatarVideoProducerAgent(BaseAgent):
    name = "avatar_video_producer"
    description = "Genera videos con avatar de IA usando HeyGen (bajo demanda)"
    max_turns = 20

    def get_tools(self) -> list[dict]:
        """Agrega tools de HeyGen para crear y verificar videos."""
        tools = self._common_tools()
        tools.extend([
            {
                "name": "create_heygen_video",
                "description": "Create an AI avatar video using HeyGen API.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "script_text": {"type": "string", "description": "The text for the avatar to speak"},
                        "language": {"type": "string", "description": "Language: 'es' or 'en'"},
                        "aspect_ratio": {"type": "string", "description": "Video aspect ratio: '9:16' or '16:9'"},
                        "title": {"type": "string", "description": "Title for the video"},
                    },
                    "required": ["script_text", "language", "title"],
                },
            },
            {
                "name": "check_heygen_video_status",
                "description": "Check the status of a HeyGen video generation request.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "video_id": {"type": "string", "description": "The HeyGen video ID to check"},
                    },
                    "required": ["video_id"],
                },
            },
        ])
        return tools

    def handle_custom_tool(self, tool_name: str, tool_input: dict) -> str:
        if tool_name == "create_heygen_video":
            return self._create_video(tool_input)
        elif tool_name == "check_heygen_video_status":
            return self._check_status(tool_input)
        return f"Unknown tool: {tool_name}"

    def _create_video(self, args: dict) -> str:
        """Crea un video con avatar en HeyGen."""
        headers = get_heygen_headers()
        avatar_id = os.getenv("HEYGEN_AVATAR_ID", "")

        if not headers.get("X-Api-Key") or "xxxxx" in headers.get("X-Api-Key", ""):
            return (
                f"[HeyGen not configured] Would create video:\n"
                f"Title: {args['title']}\n"
                f"Language: {args['language']}\n"
                f"Aspect: {args.get('aspect_ratio', '9:16')}\n"
                f"Script: {args['script_text'][:100]}...\n"
                f"Configure HEYGEN_API_KEY and HEYGEN_AVATAR_ID in .env."
            )

        if not avatar_id:
            return "Error: HEYGEN_AVATAR_ID not set in .env. Configure your avatar first at heygen.com"

        payload = {
            "video_inputs": [{
                "character": {"type": "avatar", "avatar_id": avatar_id},
                "voice": {"type": "text", "input_text": args["script_text"]},
                "background": {"type": "color", "value": "#667eea"},
            }],
            "dimension": {
                "width": 1080 if args.get("aspect_ratio") == "9:16" else 1920,
                "height": 1920 if args.get("aspect_ratio") == "9:16" else 1080,
            },
            "title": args["title"],
        }

        try:
            response = httpx.post(
                "https://api.heygen.com/v2/video/generate",
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            video_id = result.get("data", {}).get("video_id", "unknown")
            return f"HeyGen video queued. Video ID: {video_id}. Status: processing."
        except Exception as e:
            self.logger.error(f"HeyGen error: {e}")
            return f"Error creating HeyGen video: {str(e)}"

    def _check_status(self, args: dict) -> str:
        """Verifica el estado de un video en HeyGen."""
        headers = get_heygen_headers()

        try:
            response = httpx.get(
                f"https://api.heygen.com/v1/video_status.get?video_id={args['video_id']}",
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            status = result.get("data", {}).get("status", "unknown")
            video_url = result.get("data", {}).get("video_url", "")
            return f"Video status: {status}. URL: {video_url}"
        except Exception as e:
            return f"Error checking status: {str(e)}"

    def _build_prompt(self) -> str:
        return """Genera videos con avatar de IA para A&J Phygital Group usando HeyGen.

## Tu tarea:
1. Usa `read_agent_output` con agent_name="copywriter" para leer los ContentScripts
2. Identifica las piezas que requieren video con avatar (busca "visual_notes" con referencias a avatar/video)

3. Para cada video requerido:
   a. Prepara el guión adaptado para HeyGen (texto limpio, sin instrucciones de cámara)
   b. Crea el video con `create_heygen_video`
   c. Si se requiere versión bilingüe, genera en ambos idiomas
   d. Verifica el estado con `check_heygen_video_status`

4. Configuración por plataforma:
   - Reels/TikTok: aspect_ratio="9:16"
   - YouTube: aspect_ratio="16:9"
   - Fondo con color de marca (#667eea)

5. Guarda resumen usando `save_agent_output` con suffix="videos_report":
   {
     "videos_created": [
       {"slot_id": "...", "title": "...", "language": "es", "aspect_ratio": "9:16", "video_id": "...", "status": "processing"}
     ],
     "total_videos": 5,
     "pending_render": 5
   }

### Nota:
Si HEYGEN_API_KEY no está configurada, genera el reporte con los guiones
preparados para cuando se configure la API."""


def main():
    agent = AvatarVideoProducerAgent()
    result = agent.run()
    print(result)


if __name__ == "__main__":
    main()
