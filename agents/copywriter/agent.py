"""
Copywriter Agent - Escribe guiones y textos para cada pieza de contenido.
Usa Anthropic API directamente con tool_use.
"""

from agents.base import BaseAgent


class CopywriterAgent(BaseAgent):
    name = "copywriter"
    description = "Escribe guiones para podcast, reels, TikTok, YouTube, LinkedIn y descripciones"
    model = "claude-sonnet-4-20250514"  # Needs creative writing quality
    max_turns = 20

    def _build_prompt(self) -> str:
        return """Escribe todos los guiones y textos para el plan de contenido de A&J Phygital Group.

## Tu tarea:
1. Usa `read_agent_output` con agent_name="content_planner" para leer el ContentPlan aprobado
2. Usa `get_brand_guidelines` para leer las brand guidelines

3. Para CADA pieza del plan, escribe el guión completo:

   **Reels Instagram (15-60 seg):**
   - Hook (3 seg) + Desarrollo (20-40 seg) + CTA (5 seg)
   - Caption con emojis y estructura
   - ~100-150 palabras

   **Videos TikTok (15-60 seg):**
   - Hook directo (2 seg) + Contenido rápido + CTA breve
   - Caption corto y punchy
   - ~80-100 palabras

   **Posts LinkedIn (~200-300 palabras):**
   - Primera línea poderosa (hook pre-"ver más")
   - Desarrollo profesional con datos
   - Pregunta que genere conversación

   **Videos YouTube (8-15 min):**
   - Hook (30 seg) + Intro + Contenido por secciones + Recap + CTA
   - Descripción SEO con timestamps
   - ~1500-2000 palabras

   **Carruseles (5-10 slides):**
   - Cover con hook visual + título
   - Slides de contenido: un punto por slide
   - Slide final: CTA + logo
   - ~50 palabras por slide

4. Incluye notas para el Visual Designer cuando aplique (qué imagen generar)

5. Guarda usando `save_agent_output` con suffix="content_scripts":
   {
     "scripts": [
       {
         "slot_id": "2026-02-16_IG_01",
         "platform": "instagram",
         "content_type": "reel",
         "language": "es",
         "hook": "...",
         "script_body": "...",
         "cta": "...",
         "caption": "...",
         "visual_notes": "...",
         "word_count": 120,
         "estimated_duration_seconds": 45
       }
     ],
     "total_scripts": 28
   }

### Reglas:
- Framework: Hook → Problema → Solución → Prueba → CTA
- NUNCA ser genérico. Cada guión debe aportar valor específico
- Adaptar tono por plataforma (TikTok casual, LinkedIn profesional)
- Tono general: directo, orientado a resultados, innovador, profesional pero accesible
- CTAs: variar entre soft, medium y hard según la pieza
- Bilingüe: escribir en el idioma asignado por el ContentPlan"""


def main():
    agent = CopywriterAgent()
    result = agent.run()
    print(result)


if __name__ == "__main__":
    main()
