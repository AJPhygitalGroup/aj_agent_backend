"""
Brand Guardian Agent - Valida que todo el contenido cumpla con el brand kit.
Usa Anthropic API directamente con tool_use.
"""

from agents.base import BaseAgent


class BrandGuardianAgent(BaseAgent):
    name = "brand_guardian"
    description = "Valida compliance de todo el contenido con las brand guidelines"
    max_turns = 10  # Haiku: read content + check against brand guidelines

    def _build_prompt(self) -> str:
        return """Valida que TODO el contenido generado cumpla con las brand guidelines de A&J Phygital Group.

## Tu tarea:
1. Usa `get_brand_guidelines` para leer las brand guidelines completas
2. Usa `read_agent_output` con agent_name="copywriter" para leer los ContentScripts
3. Usa `read_agent_output` con agent_name="seo_hashtag_specialist" para leer las SEO optimizations

4. Para CADA pieza de contenido, evalúa con score 0-1:

   **Tono de Voz (score 0-1):**
   - ¿Es directo y orientado a resultados?
   - ¿Es profesional pero accesible?
   - ¿Adaptado a la plataforma? (LinkedIn=formal, TikTok=casual)
   - ¿Evita jerga innecesaria?

   **Consistencia de Mensajes (score 0-1):**
   - ¿Alineado con pilares de contenido?
   - ¿CTAs apropiados?
   - ¿No contradice mensajes de la marca?
   - ¿Datos verificables?

   **Riesgo de Reputación (score 0-1):**
   - ¿Podría malinterpretarse?
   - ¿Contenido ofensivo?
   - ¿Promesas irreales?
   - ¿Respeta propiedad intelectual?

   **Calidad General (score 0-1):**
   - ¿Errores ortográficos/gramaticales?
   - ¿Hashtags apropiados?
   - ¿Aporta valor real?

5. Criterios de aprobación:
   - Score >0.9: Aprobado automáticamente
   - Score 0.7-0.89: Aprobado con notas menores
   - Score 0.5-0.69: Necesita revisión
   - Score <0.5: Rechazado

6. Guarda usando `save_agent_output` con suffix="compliance_report":
   {
     "batch_score": 0.87,
     "batch_recommendation": "approved_with_notes",
     "content_reviews": [
       {
         "slot_id": "2026-02-16_IG_01",
         "voice_score": 0.9,
         "message_consistency_score": 0.85,
         "reputation_risk_score": 0.95,
         "quality_score": 0.88,
         "overall_score": 0.89,
         "status": "approved_with_notes",
         "issues": ["Minor: CTA could be stronger"],
         "suggestions": ["Consider adding a data point to support the claim"]
       }
     ],
     "critical_issues": [],
     "summary": "..."
   }

### A&J Phygital Group - Brand Key Facts:
- Tagline: "Automate. Grow. Dominate."
- Colores: #667eea (azul), #764ba2 (morado), #f093fb (rosa)
- Tono: directo, orientado a resultados, innovador, profesional pero accesible
- Servicios: AI Automations ($29+), E-commerce Consulting, Custom App Development
- NUNCA: promesas irreales, tono desesperado, descuentos excesivos, contenido genérico"""


def main():
    agent = BrandGuardianAgent()
    result = agent.run()
    print(result)


if __name__ == "__main__":
    main()
