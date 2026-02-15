# A&J Phygital Group - AI Content Generation Pipeline

## Project Overview
Sistema semi-automático de generación de contenido para marketing digital de A&J Phygital Group.
La empresa se especializa en: Automatización de procesos con IA, Aplicaciones SaaS, E-commerce Consulting.

**Objetivo:** 3-6 posts/día en múltiples plataformas (Facebook, Instagram, LinkedIn, YouTube, TikTok, Google).
**Idiomas:** Español + Inglés (contenido bilingüe).
**Modo:** Semi-automático con aprobación humana via dashboard web.

---

## Arquitectura de Agentes (12 Agentes)

### 1. Orchestrator Agent (`agents/orchestrator/`)
- **Rol:** Director de toda la orquesta de agentes
- **Responsabilidades:**
  - Coordinar la ejecución secuencial y paralela de los demás agentes
  - Gestionar el estado del pipeline (qué fase está activa)
  - Manejar errores y reintentos
  - Enviar notificaciones al dashboard para aprobación humana
  - Mantener el log de ejecución completo
- **Input:** Trigger manual o programado (cron)
- **Output:** Estado del pipeline, logs, notificaciones

### 2. Trend Researcher Agent (`agents/trend_researcher/`)
- **Rol:** Investigación de tendencias en redes sociales y Google
- **Responsabilidades:**
  - Scraping de trending topics en Facebook, Instagram, LinkedIn, YouTube, TikTok
  - Búsqueda de tendencias en Google Trends
  - Investigación con Perplexity API para contexto profundo
  - Filtrar tendencias relevantes al nicho (IA, SaaS, e-commerce, automatización)
  - Generar reporte de tendencias con ranking de relevancia
- **Input:** Nicho/keywords de la empresa, fecha actual
- **Output:** `TrendReport` (ver schemas/)
- **APIs:** Perplexity, APIs de redes sociales, Google Trends

### 3. Viral Analyzer Agent (`agents/viral_analyzer/`)
- **Rol:** Analizar la estructura de contenido viral
- **Responsabilidades:**
  - Identificar videos/posts virales del momento en el nicho
  - Analizar: tono, música, tema, tipo de video, duración, hooks
  - Extraer patrones de guiones virales (estructura narrativa)
  - Identificar formatos ganadores por plataforma
  - Generar reporte de análisis viral
- **Input:** Tendencias del Trend Researcher, URLs de contenido viral
- **Output:** `ViralAnalysisReport` (ver schemas/)
- **APIs:** YouTube Data API, TikTok API, Perplexity

### 4. Content Planner Agent (`agents/content_planner/`)
- **Rol:** Generar el plan de contenido completo
- **Responsabilidades:**
  - Crear calendario de contenido semanal/mensual
  - Asignar formatos por plataforma (reel, carrusel, podcast, video largo, etc.)
  - Definir temas y ángulos para cada pieza de contenido
  - Optimizar horarios de publicación por plataforma
  - Exportar plan a Google Sheets
- **Input:** `TrendReport` + `ViralAnalysisReport`
- **Output:** `ContentPlan` exportado a Google Sheets
- **APIs:** Google Sheets API
- **CHECKPOINT:** Requiere aprobación humana antes de continuar

### 5. Copywriter Agent (`agents/copywriter/`)
- **Rol:** Escribir todos los guiones y textos
- **Responsabilidades:**
  - Guiones para podcasts (formato conversacional/monólogo)
  - Guiones para reels de Instagram (15-60 seg)
  - Guiones para TikTok (hooks + desarrollo + CTA)
  - Guiones para videos de YouTube (largo formato)
  - Guiones para LinkedIn posts (formato profesional)
  - Descripciones/captions para cada pieza
  - CTAs adaptados por plataforma
- **Input:** `ContentPlan` aprobado, brand guidelines
- **Output:** `ContentScripts` (ver schemas/)
- **APIs:** Anthropic Claude, OpenAI

### 6. Visual Designer Agent (`agents/visual_designer/`)
- **Rol:** Generar imágenes para hooks y miniaturas
- **Responsabilidades:**
  - Crear imágenes de hooks/ganchos para videos
  - Generar miniaturas (thumbnails) para YouTube
  - Crear imágenes para posts de Instagram/Facebook
  - Mantener consistencia visual con brand kit
  - Generar variaciones A/B para testing
- **Input:** `ContentScripts`, brand assets, directrices visuales
- **Output:** Imágenes generadas en `data/outputs/images/`
- **APIs:** Flux API

### 7. Carousel Creator Agent (`agents/carousel_creator/`)
- **Rol:** Crear carruseles para LinkedIn e Instagram
- **Responsabilidades:**
  - Diseñar carruseles educativos (5-10 slides)
  - Aplicar brand guidelines en cada slide
  - Crear variaciones por plataforma (IG vs LinkedIn)
  - Exportar en formatos correctos (1080x1080, 1080x1350)
- **Input:** `ContentScripts` (tipo carrusel), brand assets
- **Output:** Carruseles en `data/outputs/carousels/`
- **APIs:** Flux API (para imágenes base)

### 8. Avatar Video Producer Agent (`agents/avatar_video_producer/`)
- **Rol:** Generar videos con avatar de IA
- **Responsabilidades:**
  - Crear videos con avatar IA usando HeyGen
  - Sincronizar audio con lip-sync
  - Aplicar branding (logos, overlays)
  - Generar versiones en español e inglés
  - Manejar cola de renderizado
- **Input:** Guiones del Copywriter, configuración de avatar
- **Output:** Videos renderizados en `data/outputs/videos/`
- **APIs:** HeyGen API
- **Nota:** Se activa bajo demanda, no en cada ciclo

### 9. SEO & Hashtag Specialist Agent (`agents/seo_hashtag_specialist/`)
- **Rol:** Optimizar SEO y hashtags para máximo alcance
- **Responsabilidades:**
  - Investigar hashtags trending por plataforma y nicho
  - Optimizar títulos y descripciones para SEO
  - Generar sets de hashtags (primarios, secundarios, long-tail)
  - Keywords research para YouTube SEO
  - Optimizar metadatos de cada pieza de contenido
- **Input:** `ContentScripts`, tendencias actuales
- **Output:** `SEOOptimizations` (ver schemas/)
- **APIs:** Perplexity, APIs de plataformas

### 10. Engagement Analyst Agent (`agents/engagement_analyst/`)
- **Rol:** Analizar métricas post-publicación
- **Responsabilidades:**
  - Monitorear engagement (likes, comments, shares, views)
  - Calcular métricas clave (engagement rate, reach, impressions)
  - Identificar contenido de alto rendimiento
  - Generar reportes de performance
  - Retroalimentar al Trend Researcher y Content Planner con insights
- **Input:** IDs de publicaciones, APIs de analytics
- **Output:** `EngagementReport` (ver schemas/)
- **APIs:** Meta Business API, YouTube Analytics, TikTok Analytics, LinkedIn Analytics

### 11. Scheduler Agent (`agents/scheduler/`)
- **Rol:** Programar publicaciones en redes sociales
- **Responsabilidades:**
  - Programar posts en horarios óptimos por plataforma
  - Subir contenido (imágenes, videos, textos) a cada plataforma
  - Manejar la cola de publicaciones
  - Confirmar publicación exitosa
  - Reprogramar en caso de fallos
- **Input:** Contenido aprobado + horarios del Content Planner
- **Output:** Confirmaciones de scheduling, IDs de publicaciones
- **APIs:** Meta Business API, TikTok API, LinkedIn API, YouTube Data API
- **CHECKPOINT:** Requiere aprobación humana antes de publicar

### 12. Brand Guardian Agent (`agents/brand_guardian/`)
- **Rol:** Validar que todo el contenido cumple con el brand kit
- **Responsabilidades:**
  - Verificar tono de voz en todos los textos
  - Validar uso correcto de colores y tipografía
  - Asegurar consistencia de mensajes con los valores de la marca
  - Revisar que no haya contenido que pueda dañar la reputación
  - Generar reporte de compliance por pieza de contenido
- **Input:** Todo el contenido generado (textos, imágenes, videos)
- **Output:** `BrandComplianceReport` (ver schemas/)

---

## Flujo de Ejecución

```
FASE 1: INVESTIGACIÓN (paralelo)
├── Trend Researcher → TrendReport
└── Viral Analyzer → ViralAnalysisReport

FASE 2: PLANIFICACIÓN
└── Content Planner → ContentPlan (→ Google Sheets)
    └── ⏸️ CHECKPOINT: Aprobación humana en Dashboard

FASE 3: CREACIÓN DE CONTENIDO (paralelo)
├── Copywriter → ContentScripts
└── SEO & Hashtag Specialist → SEOOptimizations

FASE 4: PRODUCCIÓN VISUAL (paralelo)
├── Visual Designer → Imágenes (hooks, thumbnails)
├── Carousel Creator → Carruseles
└── Avatar Video Producer → Videos (bajo demanda)

FASE 5: VALIDACIÓN
└── Brand Guardian → BrandComplianceReport
    └── ⏸️ CHECKPOINT: Aprobación humana en Dashboard

FASE 6: PUBLICACIÓN
└── Scheduler → Publicaciones programadas
    └── ⏸️ CHECKPOINT: Aprobación humana antes de publicar

FASE 7: ANÁLISIS (continuo)
└── Engagement Analyst → EngagementReport → retroalimenta FASE 1
```

---

## Estructura del Proyecto

```
agentes marketing a&J/
├── CLAUDE.md                    # Este archivo - arquitectura completa
├── ARCHITECTURE.md              # Diagramas y flujos detallados
├── README.md                    # Documentación del proyecto
├── .env.example                 # Variables de entorno template
├── config/
│   ├── config.yaml              # Configuración general
│   ├── platforms.yaml           # Config por plataforma
│   └── brand.yaml               # Brand guidelines para agentes
├── agents/
│   ├── orchestrator/
│   │   ├── agent.py
│   │   ├── prompt.md
│   │   └── __init__.py
│   ├── trend_researcher/
│   ├── viral_analyzer/
│   ├── content_planner/
│   ├── copywriter/
│   ├── visual_designer/
│   ├── carousel_creator/
│   ├── avatar_video_producer/
│   ├── seo_hashtag_specialist/
│   ├── engagement_analyst/
│   ├── scheduler/
│   └── brand_guardian/
├── schemas/
│   ├── trend_report.py
│   ├── viral_analysis.py
│   ├── content_plan.py
│   ├── content_scripts.py
│   ├── seo_optimizations.py
│   ├── engagement_report.py
│   ├── brand_compliance.py
│   └── common.py
├── prompts/
│   ├── orchestrator.md
│   ├── trend_researcher.md
│   ├── viral_analyzer.md
│   ├── content_planner.md
│   ├── copywriter.md
│   ├── visual_designer.md
│   ├── carousel_creator.md
│   ├── avatar_video_producer.md
│   ├── seo_hashtag_specialist.md
│   ├── engagement_analyst.md
│   ├── scheduler.md
│   └── brand_guardian.md
├── utils/
│   ├── logger.py
│   ├── api_clients.py
│   ├── helpers.py
│   └── constants.py
├── data/
│   ├── inputs/                  # Datos de entrada manuales
│   ├── outputs/                 # Contenido generado
│   │   ├── images/
│   │   ├── videos/
│   │   ├── carousels/
│   │   └── scripts/
│   ├── temp/                    # Archivos temporales
│   └── brand_assets/            # Logo, colores, tipografías
├── dashboard/                   # Next.js app para aprobación
├── logs/                        # Logs de ejecución
├── tests/                       # Tests unitarios e integración
└── requirements.txt             # Dependencias Python
```

---

## Convenciones de Nombres

- **Agentes:** snake_case para carpetas (`trend_researcher/`)
- **Archivos Python:** snake_case (`api_clients.py`)
- **Clases:** PascalCase (`TrendResearcherAgent`)
- **Schemas:** PascalCase para modelos (`TrendReport`)
- **Outputs:** `{agent}_{timestamp}_{type}.{ext}` (ej: `visual_designer_20260214_thumbnail_001.png`)
- **Logs:** `{agent}_{date}.log` (ej: `orchestrator_2026-02-14.log`)

---

## APIs Integradas

| API | Uso | Agente(s) |
|-----|-----|-----------|
| Anthropic Claude | Generación de texto, análisis, coordinación | Todos los agentes |
| OpenAI | Respaldo para generación, embeddings | Copywriter, Planner |
| Perplexity | Investigación profunda, tendencias | Trend Researcher, SEO |
| Flux API | Generación de imágenes | Visual Designer, Carousel Creator |
| HeyGen | Avatar de video IA | Avatar Video Producer |
| Google Sheets API | Exportación de planes de contenido | Content Planner |
| Meta Business API | Publicación FB/IG, analytics | Scheduler, Engagement Analyst |
| TikTok API | Publicación TikTok, analytics | Scheduler, Engagement Analyst |
| LinkedIn API | Publicación LinkedIn, analytics | Scheduler, Engagement Analyst |
| YouTube Data API | Publicación YouTube, analytics | Scheduler, Engagement Analyst |

---

## Checkpoints de Aprobación

1. **Post-Planificación:** Revisar el ContentPlan en Google Sheets / Dashboard antes de generar contenido
2. **Post-Producción:** Revisar todo el contenido generado (textos, imágenes, videos) antes de publicar
3. **Pre-Publicación:** Confirmar la programación final antes de que el Scheduler publique

Cada checkpoint envía notificación al dashboard y pausa el pipeline hasta recibir aprobación.
