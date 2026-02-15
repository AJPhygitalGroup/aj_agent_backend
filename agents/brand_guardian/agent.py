"""
Brand Guardian Agent - Valida que todo el contenido cumpla con el brand kit.
"""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, query

from agents.base import BaseAgent
from agents.tools import create_content_engine_tools


class BrandGuardianAgent(BaseAgent):
    name = "brand_guardian"
    description = "Valida compliance de todo el contenido con las brand guidelines"

    async def run(self) -> None:
        self.logger.info("Starting brand compliance review")

        prompt = self.load_prompt()
        tools_server = create_content_engine_tools()

        review_prompt = f"""{prompt}

## Ejecución

1. Lee las brand guidelines completas usando `get_brand_guidelines`
2. Lee los ContentScripts del copywriter: `read_agent_output` con agent_name="copywriter"
3. Lee las SEO optimizations: `read_agent_output` con agent_name="seo_hashtag_specialist"

4. Para CADA pieza de contenido, evalúa:

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

6. Genera el BrandComplianceReport:
   - Score por pieza
   - Issues críticos y menores
   - Recomendación del batch (approve/needs_revision/reject)

7. Guarda usando `save_agent_output` con agent_name="brand_guardian" y suffix="compliance_report"

### A&J Phygital Group - Brand Key Facts:
- Tagline: "Automate. Grow. Dominate."
- Colores: #667eea (azul), #764ba2 (morado), #f093fb (rosa)
- Tono: directo, orientado a resultados, innovador, profesional pero accesible
- Servicios: AI Automations ($29+), E-commerce Consulting, Custom App Development
"""

        options = ClaudeAgentOptions(
            allowed_tools=[
                "mcp__content-engine__read_agent_output",
                "mcp__content-engine__save_agent_output",
                "mcp__content-engine__get_brand_guidelines",
            ],
            mcp_servers={"content-engine": tools_server},
        )

        async for message in query(prompt=review_prompt, options=options):
            if hasattr(message, "content"):
                self.logger.info(f"BrandGuardian: {str(message.content)[:200]}")

        self.logger.info("Brand compliance review completed")


async def main():
    agent = BrandGuardianAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
