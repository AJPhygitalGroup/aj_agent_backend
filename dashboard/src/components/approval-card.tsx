'use client'

import { useState } from 'react'
import { Check, X, RotateCcw, ChevronDown, ChevronUp } from 'lucide-react'

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

interface ApprovalCardProps {
  id: string
  title: string
  subtitle: string
  platform?: string
  contentType?: string
  complianceScore?: number
  previewText?: string
  hook?: string
  checkpoint: 'post_planning' | 'post_production' | 'pre_publication'
  decidedStatus?: string
}

const platformColors: Record<string, string> = {
  instagram: 'border-l-pink-500',
  tiktok: 'border-l-gray-900',
  linkedin: 'border-l-blue-700',
  youtube: 'border-l-red-600',
  facebook: 'border-l-blue-600',
}

const platformLabels: Record<string, string> = {
  instagram: 'IG',
  tiktok: 'TT',
  linkedin: 'LI',
  youtube: 'YT',
  facebook: 'FB',
}

function ScoreBar({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const color = pct >= 80 ? 'bg-green-500' : pct >= 60 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className={`text-xs font-semibold ${
        pct >= 80 ? 'text-green-600' : pct >= 60 ? 'text-yellow-600' : 'text-red-600'
      }`}>{pct}%</span>
    </div>
  )
}

export default function ApprovalCard({
  id, title, subtitle, platform, contentType,
  complianceScore, previewText, hook, checkpoint, decidedStatus,
}: ApprovalCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [status, setStatus] = useState<string | null>(decidedStatus || null)
  const [loading, setLoading] = useState(false)

  async function handleAction(action: 'approved' | 'rejected' | 'needs_revision') {
    if (action !== 'approved' && !feedback) {
      setExpanded(true)
      return
    }
    setLoading(true)
    try {
      await fetch(`${BACKEND}/api/approvals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          checkpoint,
          item_id: id,
          status: action,
          feedback,
        }),
      })
      setStatus(action)
    } catch (err) {
      console.error('Approval failed:', err)
    }
    setLoading(false)
  }

  const borderColor = platform ? platformColors[platform] || 'border-l-gray-300' : 'border-l-brand-blue'

  return (
    <div className={`bg-white rounded-lg border border-gray-200 border-l-4 ${borderColor} shadow-sm`}>
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              {platform && (
                <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">
                  {platformLabels[platform] || platform}
                </span>
              )}
              {contentType && (
                <span className="text-xs px-1.5 py-0.5 rounded bg-brand-blue/10 text-brand-blue">
                  {contentType}
                </span>
              )}
              {status && (
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  status === 'approved' ? 'bg-green-100 text-green-700'
                    : status === 'rejected' ? 'bg-red-100 text-red-700'
                    : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {status === 'approved' ? 'Aprobado' : status === 'rejected' ? 'Rechazado' : 'Revision'}
                </span>
              )}
            </div>
            <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
            <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>
          </div>

          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1 text-gray-400 hover:text-gray-600"
          >
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>

        {/* Compliance score */}
        {complianceScore !== undefined && (
          <div className="mt-2">
            <ScoreBar score={complianceScore} />
          </div>
        )}

        {/* Hook preview */}
        {hook && (
          <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-700">
            <span className="font-semibold text-brand-purple">Hook: </span>
            {hook}
          </div>
        )}

        {/* Expanded content */}
        {expanded && (
          <div className="mt-3 space-y-3">
            {previewText && (
              <div className="p-3 bg-gray-50 rounded text-xs text-gray-700 whitespace-pre-wrap max-h-48 overflow-y-auto">
                {previewText}
              </div>
            )}

            {/* Feedback textarea */}
            <textarea
              value={feedback}
              onChange={e => setFeedback(e.target.value)}
              placeholder="Feedback o notas (requerido para rechazar)..."
              className="w-full p-2 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue/30 resize-none"
              rows={2}
            />
          </div>
        )}

        {/* Actions */}
        {!status && (
          <div className="flex gap-2 mt-3">
            <button
              onClick={() => handleAction('approved')}
              disabled={loading}
              className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-green-500 text-white hover:bg-green-600 disabled:opacity-50 transition-colors"
            >
              <Check className="w-3 h-3" /> Aprobar
            </button>
            <button
              onClick={() => handleAction('needs_revision')}
              disabled={loading}
              className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-yellow-500 text-white hover:bg-yellow-600 disabled:opacity-50 transition-colors"
            >
              <RotateCcw className="w-3 h-3" /> Revision
            </button>
            <button
              onClick={() => handleAction('rejected')}
              disabled={loading}
              className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-red-500 text-white hover:bg-red-600 disabled:opacity-50 transition-colors"
            >
              <X className="w-3 h-3" /> Rechazar
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
