"""
Viral Analyzer Agent - Analiza la estructura de contenido viral.
Usa Anthropic API directamente con tool_use.
"""

from agents.base import BaseAgent


class ViralAnalyzerAgent(BaseAgent):
    name = "viral_analyzer"
    description = "Analiza estructura, tono, música y guión de contenido viral"
    model = "claude-sonnet-4-20250514"  # Needs deep narrative analysis
    max_turns = 12

    def _build_prompt(self) -> str:
        return """Analiza la estructura de contenido viral en el nicho de A&J Phygital Group.

## Tu tarea:
1. Usa `get_brand_guidelines` para entender el nicho de la empresa
2. Usa `read_agent_output` con agent_name="trend_researcher" para leer las tendencias detectadas
3. Usa `search_perplexity` para buscar contenido viral en cada plataforma:
   - "most viral AI automation videos TikTok 2026"
   - "viral Instagram reels artificial intelligence business"
   - "top performing LinkedIn posts AI SaaS technology"
   - "viral YouTube videos AI tutorials automation 2026"
   - "Facebook viral posts about AI business tools"

4. Para cada contenido viral encontrado (mínimo 10), analiza:
   - Hook/gancho: tipo (pregunta, estadística, controversia, storytelling), texto, duración
   - Tono: educativo, entretenido, inspiracional, controversial, humorístico
   - Música/audio: trending, original, none
   - Estructura del guión: hook → desarrollo → CTA
   - Tipo de video: talking head, screen recording, B-roll, animación, text overlay
   - Métricas aproximadas: views, likes, engagement rate

5. Detecta patrones comunes entre los contenidos más exitosos:
   - Hooks más efectivos por plataforma
   - Duración ideal por formato
   - Elementos visuales recurrentes
   - CTAs que generan más engagement

6. Genera recomendaciones de formato por plataforma

7. Guarda el resultado como JSON usando `save_agent_output` con suffix="viral_analysis":
   {
     "viral_content_analyzed": [
       {
         "platform": "tiktok",
         "topic": "...",
         "hook_type": "question",
         "hook_text": "...",
         "tone": "educativo",
         "format": "talking_head",
         "estimated_views": "1M+",
         "engagement_rate": "high",
         "script_structure": "hook → problem → solution → CTA",
         "key_takeaway": "..."
       }
     ],
     "patterns_detected": [...],
     "top_hooks_by_platform": {...},
     "winning_formats_by_platform": {...},
     "recommendations": [...]
   }

Investiga en ESPAÑOL e INGLÉS. Mínimo 10 piezas de contenido viral analizadas."""


def main():
    agent = ViralAnalyzerAgent()
    result = agent.run()
    print(result)


if __name__ == "__main__":
    main()
