"""
Trend Researcher Agent - Investiga tendencias en redes sociales y Google.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.base import BaseAgent


class TrendResearcherAgent(BaseAgent):
    name = "trend_researcher"
    description = "Investiga tendencias en redes sociales y Google"
    max_turns = 20

    def _build_prompt(self) -> str:
        return """Investiga las tendencias actuales en redes sociales y Google para A&J Phygital Group.

## Tu tarea:
1. Usa `get_brand_guidelines` para entender el nicho de la empresa
2. Usa `search_perplexity` para investigar tendencias en CADA plataforma:
   - "trending topics AI automation business February 2026"
   - "tendencias Instagram reels inteligencia artificial 2026"
   - "TikTok viral videos AI SaaS technology 2026"
   - "LinkedIn trending topics artificial intelligence business automation"
   - "YouTube trending AI automation tutorials 2026"
   - "Google Trends AI chatbots e-commerce 2026"

3. Filtra por relevancia al nicho (IA, SaaS, e-commerce, automatización)
4. Genera un TrendReport JSON con esta estructura:
   {
     "platform_trends": [
       {"platform": "instagram", "trends": [{"topic": "...", "relevance_score": 0.9, "engagement_level": "high"}]},
       ...
     ],
     "top_global_trends": [...],
     "recommended_topics": ["topic1", "topic2", ...],
     "nicho_relevance_summary": "..."
   }

5. Guarda el resultado usando `save_agent_output` con suffix="trend_report"

Investiga en ESPAÑOL e INGLÉS. Mínimo 5 tendencias por plataforma."""


def main():
    agent = TrendResearcherAgent()
    result = agent.run()
    print(result)


if __name__ == "__main__":
    main()
