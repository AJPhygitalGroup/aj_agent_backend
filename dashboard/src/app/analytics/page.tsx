import { getEngagementReport } from '@/lib/data'
import { BarChart3, Eye, Heart, Share2, TrendingUp } from 'lucide-react'

export const dynamic = 'force-dynamic'

function MetricCard({ label, value, icon: Icon, color }: {
  label: string; value: string; icon: any; color: string
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${color}`}>
          <Icon className="w-4 h-4 text-white" />
        </div>
        <div>
          <p className="text-xl font-bold text-gray-900">{value}</p>
          <p className="text-xs text-gray-500">{label}</p>
        </div>
      </div>
    </div>
  )
}

function HorizontalBar({ label, value, maxValue, color }: {
  label: string; value: number; maxValue: number; color?: string
}) {
  const pct = maxValue > 0 ? Math.round((value / maxValue) * 100) : 0
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-gray-600 w-24 truncate">{label}</span>
      <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${color || 'bg-brand-gradient'}`}
          style={{ width: `${Math.max(pct, 2)}%` }}
        />
      </div>
      <span className="text-xs font-semibold text-gray-700 w-16 text-right">{value.toLocaleString()}</span>
    </div>
  )
}

export default async function AnalyticsPage() {
  const report = await getEngagementReport()

  if (!report) {
    return (
      <div className="max-w-4xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-sm text-gray-500 mt-1">Metricas de engagement post-publicacion</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
          <BarChart3 className="w-8 h-8 text-gray-300 mx-auto mb-3" />
          <h3 className="text-sm font-semibold text-gray-500">Sin datos de analytics aun</h3>
          <p className="text-xs text-gray-400 mt-1">
            Los datos apareceran despues de ejecutar la fase 7 (Engagement Analyst)
          </p>
        </div>
      </div>
    )
  }

  const platformSummary = report.platform_summary || {}
  const platforms = Object.entries(platformSummary)
  const totalReach = platforms.reduce((sum, [, p]) => sum + ((p as any).total_reach || (p as any).total_views || 0), 0)
  const totalPosts = platforms.reduce((sum, [, p]) => sum + ((p as any).posts || 0), 0)
  const maxReach = Math.max(...platforms.map(([, p]) => (p as any).total_reach || (p as any).total_views || 0), 1)

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-sm text-gray-500 mt-1">
          {report.period || 'Periodo no especificado'}
        </p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <MetricCard
          label="Engagement Rate"
          value={`${((report.overall_engagement_rate || 0) * 100).toFixed(1)}%`}
          icon={Heart}
          color="bg-brand-pink"
        />
        <MetricCard
          label="Total Reach"
          value={totalReach.toLocaleString()}
          icon={Eye}
          color="bg-brand-blue"
        />
        <MetricCard
          label="Total Posts"
          value={String(totalPosts)}
          icon={Share2}
          color="bg-brand-purple"
        />
        <MetricCard
          label="Plataformas"
          value={String(platforms.length)}
          icon={BarChart3}
          color="bg-green-500"
        />
      </div>

      {/* Platform breakdown */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm mb-8">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
          Alcance por Plataforma
        </h2>
        <div className="space-y-3">
          {platforms.map(([name, data]) => (
            <HorizontalBar
              key={name}
              label={name}
              value={(data as any).total_reach || (data as any).total_views || 0}
              maxValue={maxReach}
            />
          ))}
        </div>
      </div>

      {/* Platform table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm mb-8 overflow-hidden">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide p-6 pb-3">
          Detalle por Plataforma
        </h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100">
              <th className="text-left px-6 py-2 text-xs font-semibold text-gray-500">Plataforma</th>
              <th className="text-right px-4 py-2 text-xs font-semibold text-gray-500">Posts</th>
              <th className="text-right px-4 py-2 text-xs font-semibold text-gray-500">Engagement</th>
              <th className="text-right px-6 py-2 text-xs font-semibold text-gray-500">Reach</th>
            </tr>
          </thead>
          <tbody>
            {platforms.map(([name, data]) => (
              <tr key={name} className="border-b border-gray-50 hover:bg-gray-50">
                <td className="px-6 py-3 font-medium text-gray-900 capitalize">{name}</td>
                <td className="text-right px-4 py-3 text-gray-600">{(data as any).posts || 0}</td>
                <td className="text-right px-4 py-3 text-gray-600">
                  {(((data as any).avg_engagement || 0) * 100).toFixed(1)}%
                </td>
                <td className="text-right px-6 py-3 text-gray-600">
                  {((data as any).total_reach || (data as any).total_views || 0).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Insights */}
      {report.insights && report.insights.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm mb-8">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-4 h-4 text-brand-blue" />
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
              Insights
            </h2>
          </div>
          <ul className="space-y-2">
            {report.insights.map((insight, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-blue mt-1.5 flex-shrink-0" />
                {insight}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {report.recommendations_next_cycle && report.recommendations_next_cycle.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
            Recomendaciones para el proximo ciclo
          </h2>
          <ul className="space-y-2">
            {report.recommendations_next_cycle.map((rec, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-purple mt-1.5 flex-shrink-0" />
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
