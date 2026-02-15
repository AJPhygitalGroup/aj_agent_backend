"""
Content Planner Agent - Genera el plan de contenido semanal.
Usa Anthropic API directamente con tool_use.
"""

from agents.base import BaseAgent


class ContentPlannerAgent(BaseAgent):
    name = "content_planner"
    description = "Genera plan de contenido semanal y lo exporta a Google Sheets"
    max_turns = 25

    def _build_prompt(self) -> str:
        return """Genera un plan de contenido semanal completo para A&J Phygital Group.

## Tu tarea:
1. Usa `read_agent_output` con agent_name="trend_researcher" para leer el TrendReport
2. Usa `read_agent_output` con agent_name="viral_analyzer" para leer el ViralAnalysisReport
3. Usa `get_brand_guidelines` para leer las brand guidelines
4. Usa `get_platform_specs` para leer las specs de plataformas

5. Crea un plan de contenido para los próximos 7 días con:
   - 3-6 posts por día
   - Distribución: Instagram (2/día), TikTok (2/día), LinkedIn (1/día), Facebook (1/día), YouTube (3-4/semana)
   - Respetar los pilares de contenido:
     * 30% AI Automations & Chatbots
     * 25% SaaS & App Development
     * 20% E-commerce Consulting
     * 15% Thought Leadership
     * 10% Educación y Valor

6. Para cada pieza de contenido define:
   - Fecha y hora de publicación (formato ISO 8601)
   - Plataforma y tipo de contenido (reel, carousel, post, video, short, etc.)
   - Tema y ángulo específico
   - Idea de hook/gancho
   - Patrón viral a aplicar (del ViralAnalysisReport)
   - Idioma (ES o EN)
   - Pilar de contenido
   - Prioridad (high/medium/low)

7. Guarda el plan usando `save_agent_output` con suffix="content_plan":
   {
     "week_start": "2026-02-16",
     "week_end": "2026-02-22",
     "total_posts": 28,
     "daily_plans": [
       {
         "date": "2026-02-16",
         "content_slots": [
           {
             "slot_id": "2026-02-16_IG_01",
             "platform": "instagram",
             "content_type": "reel",
             "topic": "...",
             "hook_idea": "...",
             "viral_pattern": "...",
             "language": "es",
             "pillar": "ai_automations",
             "scheduled_time": "2026-02-16T10:00:00-05:00",
             "priority": "high"
           }
         ]
       }
     ],
     "pillar_distribution": {...},
     "platform_distribution": {...}
   }

### Reglas:
- NO repetir el mismo tema en el mismo día en diferentes plataformas
- Adaptar el ángulo a cada plataforma
- Alternar entre pilares para mantener variedad
- Incluir al menos 1 contenido educativo de alto valor por día
- Priorizar temas con tendencias rising
- Horarios óptimos por plataforma (ver platform specs)"""


def main():
    agent = ContentPlannerAgent()
    result = agent.run()
    print(result)


if __name__ == "__main__":
    main()
