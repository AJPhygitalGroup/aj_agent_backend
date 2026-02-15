# Checklist de Setup - A&J Content Engine

## Pre-requisitos

### Software
- [ ] Python 3.11+ instalado
- [ ] Node.js 18+ instalado
- [ ] Git instalado
- [ ] Claude Code CLI instalado

### APIs (obtener antes de empezar)
- [x] Anthropic API key
- [x] OpenAI API key
- [x] Perplexity API key
- [x] Flux API key
- [ ] HeyGen API key + Avatar configurado
- [ ] Google Cloud Project creado
  - [ ] Google Sheets API habilitada
  - [ ] Google Drive API habilitada
  - [ ] Service Account creada
  - [ ] JSON de credenciales descargado
- [ ] Meta Business Account
  - [ ] App creada en developers.facebook.com
  - [ ] Access token generado
  - [ ] Page ID obtenido
  - [ ] Instagram Business Account conectado
- [ ] TikTok Business Account
  - [ ] App registrada en developers.tiktok.com
  - [ ] Access token generado
- [ ] LinkedIn Developer App
  - [ ] App creada en developer.linkedin.com
  - [ ] Access token generado
  - [ ] Organization ID obtenido
- [ ] YouTube Data API
  - [ ] API habilitada en Google Cloud
  - [ ] OAuth 2.0 configurado
  - [ ] Refresh token obtenido

### Brand Assets
- [ ] Logo principal (PNG, alta resolucion)
- [ ] Logo secundario
- [ ] Logo icono/isotipo
- [ ] Colores de marca (codigos hex)
- [ ] Tipografias definidas
- [ ] Buyer personas documentados
- [ ] Tono de voz definido

---

## Pasos de Inicializacion

### Paso 1: Entorno Python
```bash
cd "C:\Users\jalej\OneDrive\Documentos\agentes marketing a&J"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Paso 2: Variables de Entorno
```bash
copy .env.example .env
# Editar .env y completar TODAS las API keys
```

### Paso 3: Google Credentials
```bash
# Copiar el archivo JSON de Service Account a:
# config/google-service-account.json

# Crear un Google Sheet y copiar su ID al .env
# GOOGLE_SHEETS_SPREADSHEET_ID=tu-id-aqui

# Compartir el Sheet con el email del Service Account
```

### Paso 4: Brand Assets
```bash
# Copiar archivos a data/brand_assets/
# - logo_primary.png
# - logo_secondary.png
# - logo_icon.png

# Actualizar config/brand.yaml con:
# - Colores reales (hex)
# - Tipografias
# - Tagline
# - Buyer personas
# - Tono de voz detallado
```

### Paso 5: Dashboard
```bash
cd dashboard
npm install
npm run dev
# Verificar que abre en http://localhost:3000
```

### Paso 6: Verificar Configuracion
```bash
# Revisar config/config.yaml
# - Ajustar timezone
# - Verificar posts_per_day
# - Revisar horarios de publicacion
# - Verificar nicho_keywords

# Revisar config/platforms.yaml
# - Confirmar que las plataformas correctas estan enabled

# Revisar config/brand.yaml
# - Completar TODOS los TODOs marcados
```

---

## Orden de Creacion de Agentes

Crear cada agente desde la terminal de Claude Code. El system prompt de cada agente esta en `prompts/{nombre}.md`.

### Fase 1: Agentes Base
```bash
# 1. Orchestrator - El cerebro que coordina todo
# Lee: prompts/orchestrator.md
# Schemas: schemas/common.py (PipelinePhase)

# 2. Brand Guardian - Define las reglas de marca
# Lee: prompts/brand_guardian.md
# Schemas: schemas/brand_compliance.py
# Config: config/brand.yaml
```

### Fase 2: Agentes de Investigacion
```bash
# 3. Trend Researcher - Investiga tendencias
# Lee: prompts/trend_researcher.md
# Schemas: schemas/trend_report.py
# APIs: Perplexity, Google Trends, APIs de redes

# 4. Viral Analyzer - Analiza contenido viral
# Lee: prompts/viral_analyzer.md
# Schemas: schemas/viral_analysis.py
# APIs: YouTube Data, TikTok, Perplexity
```

### Fase 3: Agente de Planificacion
```bash
# 5. Content Planner - Genera el plan de contenido
# Lee: prompts/content_planner.md
# Schemas: schemas/content_plan.py
# APIs: Google Sheets
# Input: TrendReport + ViralAnalysisReport
```

### Fase 4: Agentes de Creacion
```bash
# 6. Copywriter - Escribe guiones y textos
# Lee: prompts/copywriter.md
# Schemas: schemas/content_scripts.py
# APIs: Anthropic, OpenAI

# 7. SEO & Hashtag Specialist
# Lee: prompts/seo_hashtag_specialist.md
# Schemas: schemas/seo_optimizations.py
# APIs: Perplexity
```

### Fase 5: Agentes de Produccion Visual
```bash
# 8. Visual Designer - Genera imagenes
# Lee: prompts/visual_designer.md
# APIs: Flux API

# 9. Carousel Creator - Crea carruseles
# Lee: prompts/carousel_creator.md
# APIs: Flux API

# 10. Avatar Video Producer - Videos con avatar
# Lee: prompts/avatar_video_producer.md
# APIs: HeyGen
```

### Fase 6: Agentes de Publicacion y Analisis
```bash
# 11. Scheduler - Programa publicaciones
# Lee: prompts/scheduler.md
# APIs: Meta, TikTok, LinkedIn, YouTube

# 12. Engagement Analyst - Analiza metricas
# Lee: prompts/engagement_analyst.md
# Schemas: schemas/engagement_report.py
# APIs: Analytics de cada plataforma
```

---

## Verificacion Post-Setup

- [ ] Todas las API keys configuradas en .env
- [ ] Google Sheet creado y compartido
- [ ] Brand assets colocados en data/brand_assets/
- [ ] config/brand.yaml completado (sin TODOs)
- [ ] Dashboard corriendo en localhost
- [ ] Al menos el Orchestrator y Brand Guardian creados
- [ ] Pipeline ejecuta sin errores la Fase 1 (investigacion)

---

## Notas Importantes

1. **Seguridad:** NUNCA commitear el archivo .env a git
2. **Rate limits:** Respetar los limites de cada API (ver ARCHITECTURE.md)
3. **Tokens:** Configurar refresh automatico para tokens de Meta y LinkedIn
4. **HeyGen:** Configurar el avatar ANTES de crear el Avatar Video Producer
5. **Testing:** Probar cada agente individualmente antes de ejecutar el pipeline completo
