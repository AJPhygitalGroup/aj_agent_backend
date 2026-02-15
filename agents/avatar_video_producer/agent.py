"""
Avatar Video Producer Agent - Genera videos con avatar de IA via HeyGen.
Se activa bajo demanda.
"""

import asyncio
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, query, tool

from agents.base import BaseAgent
from agents.tools import create_content_engine_tools
from utils.api_clients import get_heygen_headers


@tool(
    "create_heygen_video",
    "Create an AI avatar video using HeyGen API. Provide the script text and configuration.",
    {
        "type": "object",
        "properties": {
            "script_text": {"type": "string", "description": "The text for the avatar to speak"},
            "language": {"type": "string", "description": "Language: 'es' or 'en'"},
            "aspect_ratio": {"type": "string", "description": "Video aspect ratio: '9:16' or '16:9'"},
            "title": {"type": "string", "description": "Title for the video"},
        },
        "required": ["script_text", "language", "title"],
    },
)
async def create_heygen_video(args: dict[str, Any]) -> dict[str, Any]:
    """Crea un video con avatar en HeyGen."""
    import os
    import httpx

    headers = get_heygen_headers()
    avatar_id = os.getenv("HEYGEN_AVATAR_ID", "")

    if not avatar_id:
        return {"content": [{"type": "text", "text": "Error: HEYGEN_AVATAR_ID not set in .env. Configure your avatar first at heygen.com"}]}

    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                },
                "voice": {
                    "type": "text",
                    "input_text": args["script_text"],
                },
                "background": {
                    "type": "color",
                    "value": "#667eea",
                },
            }
        ],
        "dimension": {
            "width": 1080 if args.get("aspect_ratio") == "9:16" else 1920,
            "height": 1920 if args.get("aspect_ratio") == "9:16" else 1080,
        },
        "title": args["title"],
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.heygen.com/v2/video/generate",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            video_id = result.get("data", {}).get("video_id", "unknown")
            return {"content": [{"type": "text", "text": f"HeyGen video queued. Video ID: {video_id}. Status: processing. Check status later."}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error creating HeyGen video: {str(e)}"}]}


@tool(
    "check_heygen_video_status",
    "Check the status of a HeyGen video generation request.",
    {"video_id": str},
)
async def check_heygen_video_status(args: dict[str, Any]) -> dict[str, Any]:
    """Verifica el estado de un video en HeyGen."""
    import httpx

    headers = get_heygen_headers()

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"https://api.heygen.com/v1/video_status.get?video_id={args['video_id']}",
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()
            status = result.get("data", {}).get("status", "unknown")
            video_url = result.get("data", {}).get("video_url", "")
            return {"content": [{"type": "text", "text": f"Video status: {status}. URL: {video_url}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error checking status: {str(e)}"}]}


class AvatarVideoProducerAgent(BaseAgent):
    name = "avatar_video_producer"
    description = "Genera videos con avatar de IA usando HeyGen (bajo demanda)"

    async def run(self) -> None:
        self.logger.info("Starting avatar video production")

        prompt = self.load_prompt()
        content_engine_tools = create_content_engine_tools()
        heygen_tools = create_sdk_mcp_server(
            name="heygen-tools",
            version="1.0.0",
            tools=[create_heygen_video, check_heygen_video_status],
        )

        video_prompt = f"""{prompt}

## Ejecución

1. Lee los ContentScripts del copywriter usando `read_agent_output` con agent_name="copywriter"
2. Identifica las piezas de contenido que requieren video con avatar (notas del copywriter)

3. Para cada video requerido:
   a. Prepara el guión en formato HeyGen
   b. Crea el video con `create_heygen_video`
   c. Si se requiere versión bilingüe, genera en ambos idiomas
   d. Verifica el estado con `check_heygen_video_status`

4. Configuración:
   - Aspecto 9:16 para reels/TikTok
   - Aspecto 16:9 para YouTube
   - Fondo con color de marca (#667eea)

5. Guarda resumen usando `save_agent_output` con agent_name="avatar_video_producer" y suffix="videos_report"
"""

        options = ClaudeAgentOptions(
            allowed_tools=[
                "mcp__content-engine__read_agent_output",
                "mcp__content-engine__save_agent_output",
                "mcp__heygen-tools__create_heygen_video",
                "mcp__heygen-tools__check_heygen_video_status",
            ],
            mcp_servers={
                "content-engine": content_engine_tools,
                "heygen-tools": heygen_tools,
            },
        )

        async for message in query(prompt=video_prompt, options=options):
            if hasattr(message, "content"):
                self.logger.info(f"AvatarVideoProducer: {str(message.content)[:200]}")

        self.logger.info("Avatar video production completed")


async def main():
    agent = AvatarVideoProducerAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
