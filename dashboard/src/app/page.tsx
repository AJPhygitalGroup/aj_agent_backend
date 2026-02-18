import { getPipelineState, getTrendReport } from '@/lib/data'
import PipelineStatus from '@/components/pipeline-status'
import CampaignInput from '@/components/campaign-input'
import { Zap, AlertTriangle, TrendingUp, Target } from 'lucide-react'

export const dynamic = 'force-dynamic'

function StatCard({ label, value, icon: Icon, color }: {
  label: string; value: string | number; icon: any; color: string
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${color}`}>
          <Icon className="w-4 h-4 text-white" />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-xs text-gray-500">{label}</p>
        </div>
      </div>
    </div>
  )
}

export default async function HomePage() {
  const pipeline = await getPipelineState()
  const trends = await getTrendReport()

  const phasesCompleted = pipeline.phases
    ? Object.values(pipeline.phases).filter(p =>
        (p as any).results?.every((r: any) => r.status === 'completed')
      ).length
    : 0

  const totalErrors = pipeline.errors?.length || 0
  const currentStatus = pipeline.status || 'idle'

  return (
    <div className="max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Content Engine</h1>
        <p className="text-sm text-gray-500 mt-1">
          Lanza campañas y monitorea el pipeline de A&J Phygital Group
        </p>
      </div>

      {/* Campaign Input */}
      <CampaignInput />

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <StatCard
          label="Fases completadas"
          value={`${phasesCompleted}/7`}
          icon={Zap}
          color="bg-brand-blue"
        />
        <StatCard
          label="Errores"
          value={totalErrors}
          icon={AlertTriangle}
          color={totalErrors > 0 ? 'bg-red-500' : 'bg-green-500'}
        />
        <StatCard
          label="Estado"
          value={currentStatus === 'completed' ? 'Completado' : currentStatus === 'idle' ? 'Inactivo' : 'En curso'}
          icon={Target}
          color={currentStatus === 'completed' ? 'bg-green-500' : 'bg-brand-purple'}
        />
      </div>

      {/* Pipeline Stepper */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm mb-8">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
          Progreso del Pipeline
        </h2>
        <PipelineStatus pipeline={pipeline} />
      </div>

      {/* Trends Summary */}
      {trends && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-4 h-4 text-brand-blue" />
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
              Tendencias Detectadas
            </h2>
            {trends.generation_date && (
              <span className="text-xs text-gray-400 ml-auto">{trends.generation_date}</span>
            )}
          </div>

          {trends.recommended_topics && trends.recommended_topics.length > 0 && (
            <div className="mb-4">
              <h3 className="text-xs font-semibold text-gray-500 mb-2">Temas Recomendados</h3>
              <div className="space-y-1">
                {trends.recommended_topics.slice(0, 6).map((topic, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <span className="w-5 h-5 rounded-full bg-brand-gradient text-white text-xs flex items-center justify-center font-bold">
                      {i + 1}
                    </span>
                    <span className="text-gray-700">{topic}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {trends.platform_trends && trends.platform_trends.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-gray-500 mb-2">Plataformas cubiertas</h3>
              <div className="flex flex-wrap gap-2">
                {trends.platform_trends.map(pt => (
                  <span key={pt.platform} className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-600">
                    {pt.platform} ({pt.trends?.length || 0} trends)
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!trends && currentStatus === 'idle' && (
        <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm text-center">
          <Zap className="w-8 h-8 text-gray-300 mx-auto mb-3" />
          <h3 className="text-sm font-semibold text-gray-500">Sin datos aun</h3>
          <p className="text-xs text-gray-400 mt-1">
            Escribe un brief arriba y lanza tu primera campaña
          </p>
        </div>
      )}
    </div>
  )
}
