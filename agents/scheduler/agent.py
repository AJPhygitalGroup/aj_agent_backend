"""
Scheduler Agent - Programa publicaciones en redes sociales.
"""

import asyncio
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, query, tool

from agents.base import BaseAgent
from agents.tools import create_content_engine_tools
from utils.api_clients import (
    get_linkedin_credentials,
    get_meta_access_token,
    get_tiktok_credentials,
    get_youtube_credentials,
)


@tool(
    "schedule_meta_post",
    "Schedule a post on Instagram or Facebook via Meta Business API.",
    {
        "type": "object",
        "properties": {
            "platform": {"type": "string", "enum": ["instagram", "facebook"]},
            "caption": {"type": "string"},
            "media_type": {"type": "string", "enum": ["image", "video", "carousel"]},
            "scheduled_time": {"type": "string", "description": "ISO 8601 datetime for scheduling"},
        },
        "required": ["platform", "caption", "media_type", "scheduled_time"],
    },
)
async def schedule_meta_post(args: dict[str, Any]) -> dict[str, Any]:
    """Programa un post en Instagram o Facebook."""
    token = get_meta_access_token()
    if not token:
        return {"content": [{"type": "text", "text": "Error: META_ACCESS_TOKEN not set. Configure in .env first."}]}

    # Simular scheduling (la implementación real requiere subir media primero)
    return {
        "content": [
            {
                "type": "text",
                "text": (
                    f"POST SCHEDULED (simulated):\n"
                    f"Platform: {args['platform']}\n"
                    f"Type: {args['media_type']}\n"
                    f"Time: {args['scheduled_time']}\n"
                    f"Caption: {args['caption'][:100]}...\n"
                    f"Note: Full API implementation requires media upload first. "
                    f"Configure META_ACCESS_TOKEN and META_PAGE_ID in .env."
                ),
            }
        ]
    }


@tool(
    "schedule_linkedin_post",
    "Schedule a post on LinkedIn via LinkedIn API.",
    {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "media_type": {"type": "string", "enum": ["text", "image", "video", "document"]},
            "scheduled_time": {"type": "string"},
        },
        "required": ["text", "media_type", "scheduled_time"],
    },
)
async def schedule_linkedin_post(args: dict[str, Any]) -> dict[str, Any]:
    """Programa un post en LinkedIn."""
    creds = get_linkedin_credentials()
    if not creds["access_token"]:
        return {"content": [{"type": "text", "text": "Error: LINKEDIN_ACCESS_TOKEN not set. Configure in .env first."}]}

    return {
        "content": [
            {
                "type": "text",
                "text": (
                    f"LINKEDIN POST SCHEDULED (simulated):\n"
                    f"Type: {args['media_type']}\n"
                    f"Time: {args['scheduled_time']}\n"
                    f"Text: {args['text'][:100]}..."
                ),
            }
        ]
    }


@tool(
    "schedule_tiktok_post",
    "Schedule a video post on TikTok via TikTok API.",
    {
        "type": "object",
        "properties": {
            "caption": {"type": "string"},
            "scheduled_time": {"type": "string"},
        },
        "required": ["caption", "scheduled_time"],
    },
)
async def schedule_tiktok_post(args: dict[str, Any]) -> dict[str, Any]:
    """Programa un post en TikTok."""
    creds = get_tiktok_credentials()
    if not creds["access_token"]:
        return {"content": [{"type": "text", "text": "Error: TIKTOK_ACCESS_TOKEN not set. Configure in .env first."}]}

    return {
        "content": [
            {
                "type": "text",
                "text": (
                    f"TIKTOK POST SCHEDULED (simulated):\n"
                    f"Time: {args['scheduled_time']}\n"
                    f"Caption: {args['caption'][:100]}..."
                ),
            }
        ]
    }


@tool(
    "schedule_youtube_video",
    "Schedule a video upload on YouTube via YouTube Data API.",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "tags": {"type": "string", "description": "Comma-separated tags"},
            "scheduled_time": {"type": "string"},
            "video_type": {"type": "string", "enum": ["long", "short"]},
        },
        "required": ["title", "description", "scheduled_time"],
    },
)
async def schedule_youtube_video(args: dict[str, Any]) -> dict[str, Any]:
    """Programa un video en YouTube."""
    creds = get_youtube_credentials()
    if not creds["api_key"]:
        return {"content": [{"type": "text", "text": "Error: YOUTUBE_API_KEY not set. Configure in .env first."}]}

    return {
        "content": [
            {
                "type": "text",
                "text": (
                    f"YOUTUBE VIDEO SCHEDULED (simulated):\n"
                    f"Title: {args['title']}\n"
                    f"Type: {args.get('video_type', 'long')}\n"
                    f"Time: {args['scheduled_time']}\n"
                    f"Tags: {args.get('tags', 'N/A')}"
                ),
            }
        ]
    }


class SchedulerAgent(BaseAgent):
    name = "scheduler"
    description = "Programa publicaciones en todas las redes sociales"

    async def run(self) -> None:
        self.logger.info("Starting content scheduling")

        prompt = self.load_prompt()
        content_engine_tools = create_content_engine_tools()
        scheduler_tools = create_sdk_mcp_server(
            name="scheduler-tools",
            version="1.0.0",
            tools=[
                schedule_meta_post,
                schedule_linkedin_post,
                schedule_tiktok_post,
                schedule_youtube_video,
            ],
        )

        scheduling_prompt = f"""{prompt}

## Ejecución

1. Lee el ContentPlan usando `read_agent_output` con agent_name="content_planner"
2. Lee los ContentScripts finales: `read_agent_output` con agent_name="copywriter"
3. Lee las SEO optimizations: `read_agent_output` con agent_name="seo_hashtag_specialist"
4. Lee las platform specs usando `get_platform_specs`

5. Para cada pieza de contenido aprobada:
   a. Determina la plataforma y horario del plan
   b. Programa usando el tool correspondiente:
      - Instagram/Facebook: `schedule_meta_post`
      - LinkedIn: `schedule_linkedin_post`
      - TikTok: `schedule_tiktok_post`
      - YouTube: `schedule_youtube_video`
   c. Incluye caption + hashtags del SEO specialist

6. Guarda resumen de scheduling usando `save_agent_output` con agent_name="scheduler" y suffix="schedule_report"
"""

        options = ClaudeAgentOptions(
            allowed_tools=[
                "mcp__content-engine__read_agent_output",
                "mcp__content-engine__save_agent_output",
                "mcp__content-engine__get_platform_specs",
                "mcp__scheduler-tools__schedule_meta_post",
                "mcp__scheduler-tools__schedule_linkedin_post",
                "mcp__scheduler-tools__schedule_tiktok_post",
                "mcp__scheduler-tools__schedule_youtube_video",
            ],
            mcp_servers={
                "content-engine": content_engine_tools,
                "scheduler-tools": scheduler_tools,
            },
        )

        async for message in query(prompt=scheduling_prompt, options=options):
            if hasattr(message, "content"):
                self.logger.info(f"Scheduler: {str(message.content)[:200]}")

        self.logger.info("Content scheduling completed")


async def main():
    agent = SchedulerAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
