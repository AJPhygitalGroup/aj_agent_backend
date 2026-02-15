# A&J Phygital Group - AI Content Engine

Sistema semi-automatico de generacion de contenido para marketing digital, impulsado por 12 agentes de IA coordinados.

## Que Hace

Pipeline de agentes de IA que investiga tendencias, planifica contenido, escribe guiones, genera imagenes/videos y publica automaticamente en redes sociales, con checkpoints de aprobacion humana via dashboard web.

**Target:** 3-6 posts/dia en Instagram, TikTok, LinkedIn, YouTube y Facebook.

## Requisitos Previos

### Software
- Python 3.11+
- Node.js 18+ (para el dashboard)
- Git

### Cuentas y APIs Necesarias
- [x] Anthropic API key
- [x] OpenAI API key
- [x] Perplexity API key
- [x] Flux API key (imagenes)
- [ ] HeyGen API key (avatar video)
- [ ] Google Cloud Project (Sheets API, YouTube Data API)
- [ ] Meta Business Account (Facebook + Instagram)
- [ ] TikTok Business Account + API access
- [ ] LinkedIn API credentials
- [ ] YouTube Data API credentials

## Setup Inicial

### 1. Clonar y configurar entorno

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Activar entorno (Mac/Linux)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
# Copiar template
cp .env.example .env

# Editar .env con tus API keys
# Abrir en tu editor preferido y completar TODOS los valores
```

### 3. Configurar Google Sheets API

1. Crear proyecto en Google Cloud Console
2. Habilitar Google Sheets API y Google Drive API
3. Crear Service Account y descargar JSON
4. Guardar como `config/google-service-account.json`
5. Compartir tu Google Sheet con el email del service account

### 4. Configurar APIs de Redes Sociales

Consultar la documentacion de cada plataforma:
- **Meta Business:** https://developers.facebook.com/
- **TikTok:** https://developers.tiktok.com/
- **LinkedIn:** https://developer.linkedin.com/
- **YouTube:** https://console.cloud.google.com/

### 5. Brand Assets

Colocar en `data/brand_assets/`:
- `logo_primary.png` - Logo principal
- `logo_secondary.png` - Logo secundario/monocromo
- `logo_icon.png` - Icono/isotipo

Actualizar `config/brand.yaml` con:
- Colores de marca (hex)
- Tipografias
- Tono de voz
- Buyer personas
- Tagline

### 6. Setup del Dashboard

```bash
cd dashboard
npm install
npm run dev
```

## Estructura del Proyecto

```
agentes marketing a&J/
├── CLAUDE.md              # Arquitectura completa del sistema
├── ARCHITECTURE.md        # Diagramas y flujos detallados
├── README.md              # Este archivo
├── .env.example           # Template de variables de entorno
├── .gitignore
├── requirements.txt       # Dependencias Python
│
├── config/
│   ├── config.yaml        # Configuracion general
│   ├── platforms.yaml     # Specs por plataforma
│   └── brand.yaml         # Brand guidelines
│
├── agents/                # Codigo de cada agente
│   ├── orchestrator/
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
│
├── schemas/               # Modelos Pydantic para datos entre agentes
├── prompts/               # System prompts de cada agente
├── utils/                 # Utilidades compartidas
├── data/
│   ├── inputs/            # Datos de entrada manuales
│   ├── outputs/           # Contenido generado
│   ├── temp/              # Archivos temporales
│   └── brand_assets/      # Logo, tipografia, etc.
├── dashboard/             # Next.js app para aprobacion
├── logs/                  # Logs de ejecucion
└── tests/                 # Tests
```

## Los 12 Agentes

| # | Agente | Funcion |
|---|--------|---------|
| 1 | **Orchestrator** | Coordina todo el pipeline |
| 2 | **Trend Researcher** | Investiga tendencias en 6 plataformas |
| 3 | **Viral Analyzer** | Analiza estructura de contenido viral |
| 4 | **Content Planner** | Genera plan semanal, exporta a Google Sheets |
| 5 | **Copywriter** | Escribe guiones para cada formato/plataforma |
| 6 | **Visual Designer** | Genera imagenes (hooks, thumbnails) con Flux |
| 7 | **Carousel Creator** | Crea carruseles para IG/LinkedIn |
| 8 | **Avatar Video Producer** | Videos con avatar IA via HeyGen |
| 9 | **SEO & Hashtag Specialist** | Optimiza SEO, hashtags, keywords |
| 10 | **Engagement Analyst** | Analiza metricas post-publicacion |
| 11 | **Scheduler** | Programa publicaciones en redes |
| 12 | **Brand Guardian** | Valida compliance con brand kit |

## Flujo del Pipeline

```
Investigacion → Planificacion → [APROBACION] → Creacion → Produccion Visual
→ Validacion → [APROBACION] → Scheduling → [APROBACION] → Publicacion → Analisis
```

3 checkpoints de aprobacion humana via dashboard web en Vercel.

## Orden de Creacion de Agentes

Crear los agentes en este orden desde la terminal:

```bash
# 1. Orchestrator (cerebro del sistema)
# 2. Brand Guardian (define reglas para todos)
# 3. Trend Researcher (primera fuente de datos)
# 4. Viral Analyzer (complementa investigacion)
# 5. Content Planner (depende de investigacion)
# 6. Copywriter (depende del plan)
# 7. SEO & Hashtag Specialist (paralelo al copywriter)
# 8. Visual Designer (necesita guiones)
# 9. Carousel Creator (similar al visual designer)
# 10. Avatar Video Producer (mas complejo)
# 11. Scheduler (necesita todo el contenido)
# 12. Engagement Analyst (post-publicacion)
```

## Documentacion Adicional

- `CLAUDE.md` - Arquitectura completa con detalles de cada agente
- `ARCHITECTURE.md` - Diagramas de flujo, pipeline de datos, estados
- `prompts/` - System prompts de cada agente (lectura recomendada)
- `schemas/` - Modelos de datos para comunicacion entre agentes
- `config/` - Toda la configuracion del sistema
