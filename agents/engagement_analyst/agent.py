"""
Engagement Analyst Agent - Analiza métricas post-publicación.
Usa Anthropic API directamente con tool_use.
"""

from agents.base import BaseAgent


class EngagementAnalystAgent(BaseAgent):
    name = "engagement_analyst"
    description = "Analiza métricas de engagement y genera insights accionables"
    max_turns = 20

    def _build_prompt(self) -> str:
        return """Analiza las métricas de engagement post-publicación para A&J Phygital Group.

## Tu tarea:
1. Usa `read_agent_output` con agent_name="scheduler" para leer el schedule report
2. Usa `read_agent_output` con agent_name="content_planner" para leer el content plan original
3. Usa `get_brand_guidelines` para contexto de marca

4. Para cada publicación del período:
   a. Recopilar métricas (views, likes, comments, shares, saves, reach, impressions)
   b. Calcular engagement rate por post
   c. Calcular métricas agregadas por plataforma

5. Análisis:
   - Identificar top 5 performers y bottom 5
   - ¿Qué pilar de contenido genera más engagement?
   - ¿Qué formato funciona mejor por plataforma?
   - ¿Qué horarios generan más alcance?
   - ¿Qué tipo de hook retiene más?
   - ¿Qué idioma (ES/EN) performa mejor por plataforma?

6. Generar insights accionables:
   - Recomendaciones para el próximo ciclo
   - Qué temas repetir o evitar
   - Ajustes de horarios sugeridos
   - Formatos a priorizar

7. Feedback loop - datos para retroalimentar:
   - Al Trend Researcher: qué temas funcionan
   - Al Content Planner: ajustar distribución
   - Al Copywriter: qué hooks/CTAs son más efectivos

8. Guarda usando `save_agent_output` con suffix="engagement_report":
   {
     "period": "2026-02-16 to 2026-02-22",
     "overall_engagement_rate": 0.045,
     "platform_summary": {
       "instagram": {"posts": 14, "avg_engagement": 0.05, "total_reach": 15000},
       "tiktok": {"posts": 14, "avg_engagement": 0.08, "total_views": 50000}
     },
     "top_performers": [...],
     "bottom_performers": [...],
     "pillar_performance": {...},
     "insights": [...],
     "recommendations_next_cycle": [...],
     "feedback_for_agents": {
       "trend_researcher": [...],
       "content_planner": [...],
       "copywriter": [...]
     }
   }

### Nota:
Si las APIs de analytics no están configuradas aún, genera un template del reporte
con la estructura correcta y métricas placeholder, para que sirva como referencia
cuando las APIs estén activas."""


def main():
    agent = EngagementAnalystAgent()
    result = agent.run()
    print(result)


if __name__ == "__main__":
    main()
