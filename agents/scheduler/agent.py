"""
Scheduler Agent - Programa publicaciones en redes sociales.
Usa Anthropic API directamente con tool_use.
"""

from agents.base import BaseAgent
from utils.api_clients import (
    get_linkedin_credentials,
    get_meta_access_token,
    get_tiktok_credentials,
    get_youtube_credentials,
)


class SchedulerAgent(BaseAgent):
    name = "scheduler"
    description = "Programa publicaciones en todas las redes sociales"
    max_turns = 25

    def get_tools(self) -> list[dict]:
        """Agrega tools de scheduling por plataforma."""
        tools = self._common_tools()
        tools.extend([
            {
                "name": "schedule_meta_post",
                "description": "Schedule a post on Instagram or Facebook via Meta Business API.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "enum": ["instagram", "facebook"]},
                        "caption": {"type": "string"},
                        "media_type": {"type": "string", "enum": ["image", "video", "carousel"]},
                        "scheduled_time": {"type": "string", "description": "ISO 8601 datetime"},
                    },
                    "required": ["platform", "caption", "media_type", "scheduled_time"],
                },
            },
            {
                "name": "schedule_linkedin_post",
                "description": "Schedule a post on LinkedIn via LinkedIn API.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "media_type": {"type": "string", "enum": ["text", "image", "video", "document"]},
                        "scheduled_time": {"type": "string"},
                    },
                    "required": ["text", "media_type", "scheduled_time"],
                },
            },
            {
                "name": "schedule_tiktok_post",
                "description": "Schedule a video post on TikTok.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "caption": {"type": "string"},
                        "scheduled_time": {"type": "string"},
                    },
                    "required": ["caption", "scheduled_time"],
                },
            },
            {
                "name": "schedule_youtube_video",
                "description": "Schedule a video upload on YouTube.",
                "input_schema": {
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
            },
        ])
        return tools

    def handle_custom_tool(self, tool_name: str, tool_input: dict) -> str:
        if tool_name == "schedule_meta_post":
            return self._schedule_meta(tool_input)
        elif tool_name == "schedule_linkedin_post":
            return self._schedule_linkedin(tool_input)
        elif tool_name == "schedule_tiktok_post":
            return self._schedule_tiktok(tool_input)
        elif tool_name == "schedule_youtube_video":
            return self._schedule_youtube(tool_input)
        return f"Unknown tool: {tool_name}"

    def _schedule_meta(self, args: dict) -> str:
        token = get_meta_access_token()
        if not token:
            return "Error: META_ACCESS_TOKEN not set. Configure in .env first."
        return (
            f"POST SCHEDULED (simulated):\n"
            f"Platform: {args['platform']}\n"
            f"Type: {args['media_type']}\n"
            f"Time: {args['scheduled_time']}\n"
            f"Caption: {args['caption'][:100]}...\n"
            f"Note: Full API requires media upload first. Configure META_ACCESS_TOKEN and META_PAGE_ID in .env."
        )

    def _schedule_linkedin(self, args: dict) -> str:
        creds = get_linkedin_credentials()
        if not creds["access_token"]:
            return "Error: LINKEDIN_ACCESS_TOKEN not set. Configure in .env first."
        return (
            f"LINKEDIN POST SCHEDULED (simulated):\n"
            f"Type: {args['media_type']}\n"
            f"Time: {args['scheduled_time']}\n"
            f"Text: {args['text'][:100]}..."
        )

    def _schedule_tiktok(self, args: dict) -> str:
        creds = get_tiktok_credentials()
        if not creds["access_token"]:
            return "Error: TIKTOK_ACCESS_TOKEN not set. Configure in .env first."
        return (
            f"TIKTOK POST SCHEDULED (simulated):\n"
            f"Time: {args['scheduled_time']}\n"
            f"Caption: {args['caption'][:100]}..."
        )

    def _schedule_youtube(self, args: dict) -> str:
        creds = get_youtube_credentials()
        if not creds["api_key"]:
            return "Error: YOUTUBE_API_KEY not set. Configure in .env first."
        return (
            f"YOUTUBE VIDEO SCHEDULED (simulated):\n"
            f"Title: {args['title']}\n"
            f"Type: {args.get('video_type', 'long')}\n"
            f"Time: {args['scheduled_time']}\n"
            f"Tags: {args.get('tags', 'N/A')}"
        )

    def _build_prompt(self) -> str:
        return """Programa las publicaciones de contenido de A&J Phygital Group en todas las plataformas.

## Tu tarea:
1. Usa `read_agent_output` con agent_name="content_planner" para leer el ContentPlan
2. Usa `read_agent_output` con agent_name="copywriter" para leer los ContentScripts
3. Usa `read_agent_output` con agent_name="seo_hashtag_specialist" para leer las SEO optimizations
4. Usa `get_platform_specs` para leer las specs de plataformas

5. Para cada pieza de contenido aprobada:
   a. Determina la plataforma y horario del plan
   b. Combina caption/texto + hashtags del SEO specialist
   c. Programa usando el tool correspondiente:
      - Instagram/Facebook: `schedule_meta_post`
      - LinkedIn: `schedule_linkedin_post`
      - TikTok: `schedule_tiktok_post`
      - YouTube: `schedule_youtube_video`

6. Guarda resumen usando `save_agent_output` con suffix="schedule_report":
   {
     "scheduled_posts": [
       {
         "slot_id": "...",
         "platform": "instagram",
         "scheduled_time": "2026-02-16T10:00:00-05:00",
         "media_type": "image",
         "status": "scheduled",
         "caption_preview": "..."
       }
     ],
     "total_scheduled": 28,
     "by_platform": {"instagram": 14, "tiktok": 14, ...},
     "failed": []
   }"""


def main():
    agent = SchedulerAgent()
    result = agent.run()
    print(result)


if __name__ == "__main__":
    main()
