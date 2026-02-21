"""
Scheduler Agent - Programa publicaciones en redes sociales.
Usa Meta Graph API para Facebook/Instagram, y stubs para LinkedIn/TikTok/YouTube.
"""

import os

import httpx

from agents.base import BaseAgent


class SchedulerAgent(BaseAgent):
    name = "scheduler"
    description = "Programa publicaciones en todas las redes sociales"
    max_turns = 12  # Haiku: read plan + schedule posts

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
                        "image_url": {"type": "string", "description": "Public URL of the image (required for image posts)"},
                        "scheduled_time": {"type": "string", "description": "ISO 8601 datetime for scheduling"},
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
        """Publica o programa en Facebook/Instagram via Meta Graph API."""
        token = os.getenv("META_ACCESS_TOKEN", "")
        page_id = os.getenv("META_PAGE_ID", "")
        ig_account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

        if not token or "xxxxx" in token:
            return (
                f"[Meta API not configured] Would schedule:\n"
                f"Platform: {args['platform']}, Type: {args['media_type']}\n"
                f"Time: {args['scheduled_time']}\n"
                f"Caption: {args['caption'][:100]}...\n"
                f"Configure META_ACCESS_TOKEN and META_PAGE_ID in .env"
            )

        platform = args["platform"]
        try:
            if platform == "facebook":
                if not page_id:
                    return "Error: META_PAGE_ID not set in .env"
                # Facebook Page post
                response = httpx.post(
                    f"https://graph.facebook.com/v21.0/{page_id}/feed",
                    params={"access_token": token},
                    json={"message": args["caption"]},
                    timeout=30,
                )
                response.raise_for_status()
                post_id = response.json().get("id", "unknown")
                return f"Facebook post published. Post ID: {post_id}"

            elif platform == "instagram":
                if not ig_account_id:
                    return "Error: INSTAGRAM_BUSINESS_ACCOUNT_ID not set in .env"
                image_url = args.get("image_url", "")
                if not image_url:
                    return (
                        f"[Instagram requires image_url] Scheduled (simulated):\n"
                        f"Caption: {args['caption'][:100]}...\n"
                        f"Time: {args['scheduled_time']}\n"
                        f"Note: Provide a public image_url for real publishing."
                    )
                # Step 1: Create media container
                container_resp = httpx.post(
                    f"https://graph.facebook.com/v21.0/{ig_account_id}/media",
                    params={"access_token": token},
                    json={"image_url": image_url, "caption": args["caption"]},
                    timeout=30,
                )
                container_resp.raise_for_status()
                creation_id = container_resp.json().get("id")

                # Step 2: Publish
                publish_resp = httpx.post(
                    f"https://graph.facebook.com/v21.0/{ig_account_id}/media_publish",
                    params={"access_token": token},
                    json={"creation_id": creation_id},
                    timeout=30,
                )
                publish_resp.raise_for_status()
                post_id = publish_resp.json().get("id", "unknown")
                return f"Instagram post published. Post ID: {post_id}"

        except httpx.HTTPStatusError as e:
            error_body = e.response.text[:300]
            self.logger.error(f"Meta API error: {error_body}")
            return f"Meta API error ({e.response.status_code}): {error_body}"
        except Exception as e:
            self.logger.error(f"Meta scheduling error: {e}")
            return f"Error: {str(e)}"

        return "Unknown platform"

    def _schedule_linkedin(self, args: dict) -> str:
        token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        if not token or "xxxxx" in token:
            return (
                f"[LinkedIn API not configured] Would schedule:\n"
                f"Type: {args['media_type']}, Time: {args['scheduled_time']}\n"
                f"Text: {args['text'][:100]}...\n"
                f"Configure LINKEDIN_ACCESS_TOKEN in .env"
            )
        org_id = os.getenv("LINKEDIN_ORGANIZATION_ID", "")
        try:
            author = f"urn:li:organization:{org_id}" if org_id else "urn:li:person:me"
            response = httpx.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
                json={
                    "author": author,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": args["text"]},
                            "shareMediaCategory": "NONE",
                        }
                    },
                    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
                },
                timeout=30,
            )
            response.raise_for_status()
            return f"LinkedIn post published. Response: {response.json()}"
        except Exception as e:
            self.logger.error(f"LinkedIn error: {e}")
            return f"LinkedIn error: {str(e)}"

    def _schedule_tiktok(self, args: dict) -> str:
        token = os.getenv("TIKTOK_ACCESS_TOKEN", "")
        if not token or "xxxxx" in token:
            return (
                f"[TikTok API not configured] Would schedule:\n"
                f"Time: {args['scheduled_time']}\n"
                f"Caption: {args['caption'][:100]}...\n"
                f"Configure TIKTOK_ACCESS_TOKEN in .env"
            )
        return (
            f"TIKTOK POST SCHEDULED (pending video upload):\n"
            f"Time: {args['scheduled_time']}\n"
            f"Caption: {args['caption'][:100]}...\n"
            f"Note: TikTok Content Publishing API requires video upload first."
        )

    def _schedule_youtube(self, args: dict) -> str:
        token = os.getenv("YOUTUBE_API_KEY", "")
        if not token or "xxxxx" in token:
            return (
                f"[YouTube API not configured] Would schedule:\n"
                f"Title: {args['title']}\n"
                f"Type: {args.get('video_type', 'long')}\n"
                f"Time: {args['scheduled_time']}\n"
                f"Configure YOUTUBE_API_KEY in .env"
            )
        return (
            f"YOUTUBE VIDEO SCHEDULED (pending video upload):\n"
            f"Title: {args['title']}\n"
            f"Type: {args.get('video_type', 'long')}\n"
            f"Time: {args['scheduled_time']}\n"
            f"Note: YouTube Data API requires OAuth2 + video file upload."
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
