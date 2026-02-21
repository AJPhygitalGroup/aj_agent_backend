"""
SEO & Hashtag Specialist Agent - Optimiza SEO, hashtags y keywords.
Usa Anthropic API directamente con tool_use.
"""

from agents.base import BaseAgent


class SEOHashtagSpecialistAgent(BaseAgent):
    name = "seo_hashtag_specialist"
    description = "Optimiza SEO, hashtags y keywords para máximo alcance orgánico"
    max_turns = 12  # Haiku: read scripts + generate hashtags/keywords

    def _build_prompt(self) -> str:
        return """Optimiza SEO, hashtags y keywords para todo el contenido de A&J Phygital Group.

## Tu tarea:
1. Usa `read_agent_output` con agent_name="copywriter" para leer los ContentScripts
2. Usa `get_brand_guidelines` para leer las brand guidelines
3. Usa `search_perplexity` para investigar hashtags trending:
   - "trending hashtags AI automation Instagram 2026"
   - "best hashtags TikTok artificial intelligence business"
   - "LinkedIn hashtags SaaS technology trending"
   - "YouTube SEO tags AI automation tutorials"
   - "hashtags tendencia inteligencia artificial negocios"

4. Para CADA pieza de contenido:
   a. Genera set de hashtags (3 niveles):
      - Primarios (alto volumen, 500K+ posts)
      - Secundarios (nicho medio, 50K-500K)
      - Long-tail (específicos, <50K)
   b. Incluye hashtags de marca: #AJPhygitalGroup, #AutomateGrowDominate
   c. Optimiza título para SEO
   d. Optimiza descripción con keywords naturales
   e. Genera alt text para imágenes
   f. Para YouTube: genera tags y keywords research

5. Cantidades por plataforma:
   - Instagram: hasta 25 hashtags
   - TikTok: 3-5 hashtags
   - LinkedIn: 3-5 hashtags
   - YouTube: 10-15 tags
   - Facebook: 3-5 hashtags

6. Identifica keyword opportunities (alto volumen, baja competencia)

7. Guarda usando `save_agent_output` con suffix="seo_optimizations":
   {
     "optimizations": [
       {
         "slot_id": "2026-02-16_IG_01",
         "platform": "instagram",
         "hashtags": {
           "primary": ["#AI", "#Automation", ...],
           "secondary": ["#AIBusiness", ...],
           "long_tail": ["#AIAutomationForSMB", ...],
           "branded": ["#AJPhygitalGroup", "#AutomateGrowDominate"]
         },
         "optimized_title": "...",
         "optimized_description": "...",
         "alt_text": "...",
         "keywords": ["...", "..."]
       }
     ],
     "keyword_opportunities": [...],
     "trending_hashtags_by_platform": {...}
   }

### Reglas:
- NO usar hashtags baneados o shadowbanned
- NO repetir exactamente el mismo set de hashtags en posts consecutivos
- Priorizar hashtags en el idioma del contenido
- Incluir mix de hashtags en ES + EN para alcance máximo"""


def main():
    agent = SEOHashtagSpecialistAgent()
    result = agent.run()
    print(result)


if __name__ == "__main__":
    main()
