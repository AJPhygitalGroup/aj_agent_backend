# Arquitectura del Pipeline - A&J Phygital Group Content Engine

## Diagrama de Flujo General

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR AGENT                          │
│                   (Coordina todo el pipeline)                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     FASE 1: INVESTIGACIÓN                           │
│                        (En paralelo)                                │
│                                                                     │
│  ┌─────────────────────┐     ┌──────────────────────┐               │
│  │  TREND RESEARCHER   │     │   VIRAL ANALYZER     │               │
│  │                     │     │                      │               │
│  │ - Google Trends     │     │ - Estructura videos  │               │
│  │ - Facebook trends   │     │ - Tono y música      │               │
│  │ - Instagram trends  │     │ - Hooks/ganchos      │               │
│  │ - LinkedIn trends   │     │ - Patrones guiones   │               │
│  │ - YouTube trends    │     │ - Formatos ganadores  │               │
│  │ - TikTok trends     │     │                      │               │
│  │ - Perplexity search │     │                      │               │
│  └────────┬────────────┘     └──────────┬───────────┘               │
│           │                             │                           │
│           └──────────┬──────────────────┘                           │
│                      ▼                                              │
│              TrendReport +                                          │
│           ViralAnalysisReport                                       │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    FASE 2: PLANIFICACIÓN                             │
│                                                                     │
│  ┌──────────────────────────────────────┐                            │
│  │        CONTENT PLANNER              │                            │
│  │                                     │                            │
│  │ - Calendario semanal/mensual        │                            │
│  │ - Asignación formato x plataforma   │                            │
│  │ - Temas y ángulos por pieza         │                            │
│  │ - Horarios óptimos                  │                            │
│  │ - Exporta a Google Sheets           │                            │
│  └──────────────────┬──────────────────┘                            │
│                     │                                               │
│                     ▼                                               │
│           ┌─────────────────┐                                       │
│           │  ContentPlan    │──────► Google Sheets                   │
│           └─────────────────┘                                       │
│                     │                                               │
│          ┌──────────▼──────────┐                                    │
│          │  ⏸️ CHECKPOINT #1   │                                    │
│          │  Aprobación humana  │◄──── Dashboard Web (Vercel)        │
│          │  del plan           │                                    │
│          └──────────┬──────────┘                                    │
└─────────────────────┼──────────────────────────────────────────────┘
                      │ (Aprobado)
                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                FASE 3: CREACIÓN DE CONTENIDO                        │
│                      (En paralelo)                                  │
│                                                                     │
│  ┌─────────────────────┐     ┌──────────────────────────┐           │
│  │    COPYWRITER       │     │  SEO & HASHTAG SPECIALIST│           │
│  │                     │     │                          │           │
│  │ - Guiones podcast   │     │ - Hashtags trending      │           │
│  │ - Guiones reels IG  │     │ - SEO títulos/desc       │           │
│  │ - Guiones TikTok    │     │ - Keywords YouTube       │           │
│  │ - Guiones YouTube   │     │ - Meta tags              │           │
│  │ - Posts LinkedIn     │     │ - Sets hashtags          │           │
│  │ - Descripciones     │     │   (primary/secondary)    │           │
│  │ - CTAs              │     │                          │           │
│  └────────┬────────────┘     └───────────┬──────────────┘           │
│           │                              │                          │
│           └──────────┬───────────────────┘                          │
│                      ▼                                              │
│           ContentScripts +                                          │
│           SEOOptimizations                                          │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│               FASE 4: PRODUCCIÓN VISUAL                             │
│                    (En paralelo)                                     │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ VISUAL DESIGNER │  │CAROUSEL CREATOR │  │AVATAR VIDEO PRODUCER│  │
│  │                 │  │                 │  │                     │  │
│  │ - Hook images   │  │ - Carruseles IG │  │ - Videos con avatar │  │
│  │ - Thumbnails YT │  │ - Carruseles LI │  │ - Lip-sync          │  │
│  │ - Post images   │  │ - 5-10 slides   │  │ - ES + EN           │  │
│  │ - Variaciones   │  │ - Brand applied │  │ - (Bajo demanda)    │  │
│  │   A/B testing   │  │                 │  │                     │  │
│  └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘  │
│           │                    │                      │             │
│           └────────────────────┼──────────────────────┘             │
│                                ▼                                    │
│                       Assets visuales                               │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    FASE 5: VALIDACIÓN                                │
│                                                                     │
│  ┌──────────────────────────────────────┐                            │
│  │        BRAND GUARDIAN               │                            │
│  │                                     │                            │
│  │ - Verifica tono de voz              │                            │
│  │ - Valida colores/tipografía         │                            │
│  │ - Consistencia de mensajes          │                            │
│  │ - Review de reputación              │                            │
│  │ - Compliance report                 │                            │
│  └──────────────────┬──────────────────┘                            │
│                     │                                               │
│          ┌──────────▼──────────┐                                    │
│          │  ⏸️ CHECKPOINT #2   │                                    │
│          │  Aprobación humana  │◄──── Dashboard Web (Vercel)        │
│          │  del contenido      │                                    │
│          └──────────┬──────────┘                                    │
└─────────────────────┼──────────────────────────────────────────────┘
                      │ (Aprobado)
                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   FASE 6: PUBLICACIÓN                                │
│                                                                     │
│  ┌──────────────────────────────────────┐                            │
│  │          SCHEDULER                  │                            │
│  │                                     │                            │
│  │ - Programa posts FB/IG (Meta API)   │                            │
│  │ - Programa posts TikTok             │                            │
│  │ - Programa posts LinkedIn           │                            │
│  │ - Programa videos YouTube           │                            │
│  │ - Cola de publicaciones             │                            │
│  │ - Confirmación de publicación       │                            │
│  └──────────────────┬──────────────────┘                            │
│                     │                                               │
│          ┌──────────▼──────────┐                                    │
│          │  ⏸️ CHECKPOINT #3   │                                    │
│          │  Confirmar schedule │◄──── Dashboard Web (Vercel)        │
│          │  antes de publicar  │                                    │
│          └──────────┬──────────┘                                    │
└─────────────────────┼──────────────────────────────────────────────┘
                      │ (Confirmado)
                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│               FASE 7: ANÁLISIS (Continuo)                           │
│                                                                     │
│  ┌──────────────────────────────────────┐                            │
│  │      ENGAGEMENT ANALYST             │                            │
│  │                                     │                            │
│  │ - Monitorea engagement              │                            │
│  │ - Métricas: likes, shares, views    │                            │
│  │ - Engagement rate, reach            │                            │
│  │ - Identifica top performers         │                            │
│  │ - Reportes de performance           │                            │
│  │                                     │                            │
│  │        ┌─────────────┐              │                            │
│  │        │ FEEDBACK    │──────────────────► Retroalimenta FASE 1   │
│  │        │ LOOP        │              │                            │
│  │        └─────────────┘              │                            │
│  └─────────────────────────────────────┘                            │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Pipeline de Datos entre Agentes

### Schemas de Comunicación

Cada agente produce y consume datos estructurados (Pydantic models):

```
TrendResearcher ──► TrendReport ──┐
                                  ├──► ContentPlanner ──► ContentPlan
ViralAnalyzer ──► ViralAnalysis ──┘                          │
                                                             ▼
                                              ┌──── Copywriter ──► ContentScripts
                                              │
                                    ContentPlan (aprobado)
                                              │
                                              └──── SEOSpecialist ──► SEOOptimizations
                                                                          │
                                              ┌───────────────────────────┘
                                              ▼
                                    ContentScripts + SEOOptimizations
                                              │
                                    ┌─────────┼──────────┐
                                    ▼         ▼          ▼
                              VisualDesigner  Carousel  AvatarVideo
                                    │         │          │
                                    └─────────┼──────────┘
                                              ▼
                                       All Content
                                              │
                                              ▼
                                       BrandGuardian ──► BrandComplianceReport
                                              │
                                              ▼ (aprobado)
                                         Scheduler ──► Publicaciones
                                              │
                                              ▼
                                     EngagementAnalyst ──► EngagementReport
                                              │
                                              └──► Retroalimenta TrendResearcher
```

---

## Comunicación entre Agentes

### Método de comunicación: File-based + State Machine

Los agentes se comunican mediante:
1. **Archivos JSON** en `data/outputs/` con schemas validados por Pydantic
2. **State Machine** gestionado por el Orchestrator que controla qué agente se ejecuta
3. **Dashboard API** para checkpoints de aprobación humana

### Estado del Pipeline

```python
class PipelineState:
    IDLE = "idle"
    RESEARCHING = "researching"          # Fase 1
    PLANNING = "planning"                # Fase 2
    AWAITING_PLAN_APPROVAL = "awaiting_plan_approval"
    CREATING_CONTENT = "creating_content" # Fase 3
    PRODUCING_VISUALS = "producing_visuals" # Fase 4
    VALIDATING = "validating"            # Fase 5
    AWAITING_CONTENT_APPROVAL = "awaiting_content_approval"
    SCHEDULING = "scheduling"            # Fase 6
    AWAITING_SCHEDULE_APPROVAL = "awaiting_schedule_approval"
    PUBLISHED = "published"              # Fase 6 completada
    ANALYZING = "analyzing"              # Fase 7
    COMPLETED = "completed"
    ERROR = "error"
```

---

## Arquitectura del Dashboard

```
┌─────────────────────────────────────────────────┐
│              DASHBOARD (Next.js + Vercel)         │
│                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │  Pipeline   │  │  Content   │  │  Analytics │  │
│  │  Status     │  │  Review    │  │  Overview  │  │
│  └────────────┘  └────────────┘  └────────────┘  │
│                                                   │
│  ┌────────────────────────────────────────────┐   │
│  │         Approval Queue                     │   │
│  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐      │   │
│  │  │Reel │  │Post │  │Video│  │Caru.│      │   │
│  │  │ ✅❌ │  │ ✅❌ │  │ ✅❌ │  │ ✅❌ │      │   │
│  │  └─────┘  └─────┘  └─────┘  └─────┘      │   │
│  └────────────────────────────────────────────┘   │
│                                                   │
│  ┌────────────────────────────────────────────┐   │
│  │         Schedule Calendar                  │   │
│  │  Lun | Mar | Mie | Jue | Vie | Sab | Dom  │   │
│  │  IG  | TT  | LI  | YT  | IG  | FB  | ALL  │   │
│  └────────────────────────────────────────────┘   │
│                                                   │
│  Backend API: /api/approve, /api/status,          │
│  /api/content, /api/schedule, /api/analytics      │
└─────────────────────────────────────────────────┘
```

---

## Orden Recomendado para Crear los Agentes

1. **Orchestrator** - Es el cerebro, debe existir primero
2. **Brand Guardian** - Define las reglas que todos deben seguir
3. **Trend Researcher** - Primera fuente de datos
4. **Viral Analyzer** - Complementa la investigación
5. **Content Planner** - Depende de los anteriores
6. **Copywriter** - Depende del plan aprobado
7. **SEO & Hashtag Specialist** - Trabaja en paralelo con Copywriter
8. **Visual Designer** - Necesita los guiones
9. **Carousel Creator** - Similar al Visual Designer
10. **Avatar Video Producer** - Más complejo, se crea después
11. **Scheduler** - Necesita todo el contenido listo
12. **Engagement Analyst** - Solo relevante post-publicación

---

## Consideraciones Técnicas

### Rate Limits
- **Meta API:** ~200 calls/hora (publicación)
- **TikTok API:** Varía según nivel de acceso
- **LinkedIn API:** ~100 calls/día para publicación
- **YouTube API:** 10,000 unidades/día
- **HeyGen:** Depende del plan contratado
- **Flux API:** Depende del plan

### Manejo de Errores
- Cada agente implementa retry con exponential backoff
- El Orchestrator registra errores y puede saltar fases no críticas
- Logs detallados en `logs/` para debugging
- Notificaciones de error al dashboard

### Seguridad
- API keys en `.env` (nunca en código)
- Tokens de redes sociales con refresh automático
- Dashboard protegido con autenticación básica
- Datos sensibles excluidos de git via `.gitignore`
