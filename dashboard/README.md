# Dashboard de Aprobacion - Content Engine

Dashboard web en Next.js para revisar y aprobar contenido generado por los agentes.

## Setup

```bash
cd dashboard
npm install
npm run dev
```

Abrir http://localhost:3000

## Deploy en Vercel

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel
```

## Funcionalidades Planificadas

- [ ] Vista del estado del pipeline en tiempo real
- [ ] Cola de aprobacion con preview de contenido
- [ ] Calendario de publicaciones
- [ ] Metricas de engagement
- [ ] Aprobacion/rechazo de piezas individuales
- [ ] Vista previa de imagenes, carruseles y videos
- [ ] Edicion rapida de textos antes de aprobar
- [ ] Historial de publicaciones

## API Endpoints

- `GET /api/status` - Estado del pipeline
- `GET /api/content` - Contenido pendiente de aprobacion
- `POST /api/approve` - Aprobar/rechazar contenido
- `GET /api/schedule` - Ver schedule de publicaciones
- `POST /api/schedule/confirm` - Confirmar schedule
- `GET /api/analytics` - Metricas de engagement
