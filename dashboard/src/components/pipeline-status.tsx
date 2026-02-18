import type { PipelineState } from '@/lib/data'
import { CheckCircle, Circle, AlertCircle, Loader2, ShieldCheck } from 'lucide-react'

const PHASES = [
  { num: 1, name: 'Investigacion', agents: ['trend_researcher', 'viral_analyzer'] },
  { num: 2, name: 'Planificacion', agents: ['content_planner'], checkpoint: true },
  { num: 3, name: 'Creacion de Contenido', agents: ['copywriter', 'seo_hashtag_specialist'] },
  { num: 4, name: 'Produccion Visual', agents: ['visual_designer', 'carousel_creator'] },
  { num: 5, name: 'Validacion', agents: ['brand_guardian'], checkpoint: true },
  { num: 6, name: 'Publicacion', agents: ['scheduler'], checkpoint: true },
  { num: 7, name: 'Analisis', agents: ['engagement_analyst'] },
]

function getPhaseStatus(
  phaseNum: number,
  pipeline: PipelineState
): 'completed' | 'active' | 'error' | 'pending' {
  const completed = pipeline.agents_completed || []
  const phaseInfo = pipeline.phases?.[String(phaseNum)]

  if (phaseInfo) {
    const results = phaseInfo.results || []
    const hasError = results.some(r => r.status === 'error')
    if (hasError) return 'error'
    const allDone = results.every(r => r.status === 'completed')
    if (allDone) return 'completed'
  }

  const currentPhase = pipeline.phase || 0
  if (phaseNum === currentPhase) return 'active'
  if (phaseNum < currentPhase) return 'completed'

  return 'pending'
}

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case 'completed':
      return <CheckCircle className="w-5 h-5 text-green-500" />
    case 'active':
      return <Loader2 className="w-5 h-5 text-brand-blue animate-spin" />
    case 'error':
      return <AlertCircle className="w-5 h-5 text-red-500" />
    default:
      return <Circle className="w-5 h-5 text-gray-300" />
  }
}

export default function PipelineStatus({ pipeline }: { pipeline: PipelineState }) {
  return (
    <div className="space-y-2">
      {PHASES.map((phase, idx) => {
        const status = getPhaseStatus(phase.num, pipeline)
        return (
          <div key={phase.num} className="flex items-start gap-4">
            {/* Timeline */}
            <div className="flex flex-col items-center">
              <StatusIcon status={status} />
              {idx < PHASES.length - 1 && (
                <div className={`w-0.5 h-8 mt-1 ${
                  status === 'completed' ? 'bg-green-300' : 'bg-gray-200'
                }`} />
              )}
            </div>

            {/* Content */}
            <div className={`flex-1 pb-4 ${status === 'pending' ? 'opacity-50' : ''}`}>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-gray-400">FASE {phase.num}</span>
                {phase.checkpoint && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full bg-amber-100 text-amber-700">
                    <ShieldCheck className="w-3 h-3" />
                    Checkpoint
                  </span>
                )}
              </div>
              <h3 className={`text-sm font-semibold mt-0.5 ${
                status === 'active' ? 'text-brand-blue' : 'text-gray-800'
              }`}>
                {phase.name}
              </h3>
              <div className="flex flex-wrap gap-1 mt-1">
                {phase.agents.map(agent => {
                  const agentCompleted = (pipeline.agents_completed || []).includes(agent)
                  const phaseResults = pipeline.phases?.[String(phase.num)]?.results || []
                  const agentResult = phaseResults.find(r => r.agent === agent)
                  const agentError = agentResult?.status === 'error'

                  return (
                    <span
                      key={agent}
                      className={`text-xs px-2 py-0.5 rounded ${
                        agentError
                          ? 'bg-red-100 text-red-700'
                          : agentCompleted || agentResult?.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-500'
                      }`}
                    >
                      {agent.replace(/_/g, ' ')}
                    </span>
                  )
                })}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
