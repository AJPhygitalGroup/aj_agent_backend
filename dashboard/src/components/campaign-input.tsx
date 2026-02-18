'use client'

import { useState, useEffect, useCallback } from 'react'
import { Rocket, Loader2, CheckCircle, XCircle, RefreshCw } from 'lucide-react'

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

const ALL_PLATFORMS = [
  { id: 'instagram', label: 'Instagram', emoji: '📸' },
  { id: 'tiktok', label: 'TikTok', emoji: '🎵' },
  { id: 'linkedin', label: 'LinkedIn', emoji: '💼' },
  { id: 'youtube', label: 'YouTube', emoji: '🎬' },
  { id: 'facebook', label: 'Facebook', emoji: '📘' },
]

const LANGUAGES = [
  { id: 'es', label: 'Español' },
  { id: 'en', label: 'English' },
]

type CampaignStatus = 'idle' | 'running' | 'completed' | 'stopped' | 'error'

interface CampaignState {
  status: CampaignStatus
  brief?: string
  phase?: number
  phase_name?: string
  campaign_brief?: string
}

export default function CampaignInput() {
  const [brief, setBrief] = useState('')
  const [platforms, setPlatforms] = useState<string[]>(['instagram', 'tiktok', 'linkedin', 'youtube', 'facebook'])
  const [languages, setLanguages] = useState<string[]>(['es', 'en'])
  const [campaignState, setCampaignState] = useState<CampaignState>({ status: 'idle' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // Poll campaign status
  const pollStatus = useCallback(async () => {
    try {
      const res = await fetch(`${BACKEND}/api/campaigns`)
      const data = await res.json()
      const pipelineStatus = data.pipeline?.status || 'idle'
      const campaignData = data.campaign

      if (campaignData?.status === 'running' || pipelineStatus === 'running') {
        setCampaignState({
          status: 'running',
          brief: campaignData?.brief,
          phase: data.pipeline?.phase,
          phase_name: data.pipeline?.phase_name,
          campaign_brief: data.pipeline?.campaign_brief,
        })
      } else if (pipelineStatus === 'completed' && campaignData) {
        setCampaignState({
          status: 'completed',
          brief: campaignData?.brief,
          phase: data.pipeline?.phase,
        })
      } else if (pipelineStatus === 'stopped_by_user') {
        setCampaignState({
          status: 'stopped',
          brief: campaignData?.brief,
        })
      } else {
        setCampaignState({ status: 'idle' })
      }
    } catch {
      // silently ignore polling errors
    }
  }, [])

  useEffect(() => {
    pollStatus()
    const interval = setInterval(pollStatus, 5000)
    return () => clearInterval(interval)
  }, [pollStatus])

  const togglePlatform = (id: string) => {
    setPlatforms(prev =>
      prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]
    )
  }

  const toggleLanguage = (id: string) => {
    setLanguages(prev =>
      prev.includes(id) ? prev.filter(l => l !== id) : [...prev, id]
    )
  }

  const handleSubmit = async () => {
    if (!brief.trim() || platforms.length === 0 || languages.length === 0) return
    setError('')
    setSubmitting(true)

    try {
      const res = await fetch(`${BACKEND}/api/campaigns`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brief: brief.trim(), platforms, language: languages }),
      })

      const data = await res.json()

      if (!res.ok) {
        setError(data.error || 'Error al lanzar la campaña')
        return
      }

      setCampaignState({ status: 'running', brief: brief.trim() })
      setBrief('')
    } catch (e) {
      setError('Error de conexión')
    } finally {
      setSubmitting(false)
    }
  }

  const handleReset = async () => {
    setCampaignState({ status: 'idle' })
  }

  // ── Running state ──
  if (campaignState.status === 'running') {
    return (
      <div className="bg-white rounded-xl border border-brand-blue/30 p-6 shadow-sm mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-lg bg-brand-gradient">
            <Loader2 className="w-5 h-5 text-white animate-spin" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-gray-900">Campaña en ejecución</h2>
            <p className="text-sm text-gray-500">{campaignState.brief || campaignState.campaign_brief}</p>
          </div>
        </div>

        {/* Progress */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Fase {campaignState.phase || 0} de 7</span>
            <span>{campaignState.phase_name || 'Iniciando...'}</span>
          </div>
          <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-brand-gradient rounded-full transition-all duration-700"
              style={{ width: `${Math.max(((campaignState.phase || 0) / 7) * 100, 5)}%` }}
            />
          </div>
        </div>

        <p className="text-xs text-gray-400 mt-3">
          Actualizando cada 5 segundos... Los checkpoints aparecerán en la pestaña Approvals.
        </p>
      </div>
    )
  }

  // ── Completed state ──
  if (campaignState.status === 'completed') {
    return (
      <div className="bg-white rounded-xl border border-green-200 p-6 shadow-sm mb-8">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-green-500">
            <CheckCircle className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-bold text-gray-900">Campaña completada</h2>
            <p className="text-sm text-gray-500">{campaignState.brief}</p>
          </div>
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-brand-blue hover:bg-brand-blue/5 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Nueva campaña
          </button>
        </div>
      </div>
    )
  }

  // ── Stopped state ──
  if (campaignState.status === 'stopped') {
    return (
      <div className="bg-white rounded-xl border border-yellow-200 p-6 shadow-sm mb-8">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-yellow-500">
            <XCircle className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-bold text-gray-900">Campaña detenida</h2>
            <p className="text-sm text-gray-500">{campaignState.brief}</p>
          </div>
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-brand-blue hover:bg-brand-blue/5 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Nueva campaña
          </button>
        </div>
      </div>
    )
  }

  // ── Idle state: input form ──
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm mb-8">
      <h2 className="text-lg font-bold text-gray-900 mb-1">Nueva Campaña</h2>
      <p className="text-sm text-gray-500 mb-4">
        Describe tu campaña y los agentes harán el resto
      </p>

      {/* Brief textarea */}
      <textarea
        value={brief}
        onChange={e => setBrief(e.target.value)}
        placeholder="Ej: Desarrolla una campaña completa de marketing digital para un restaurante italiano en Miami, enfocada en atraer millennials con contenido sobre la experiencia gastronómica..."
        className="w-full h-28 px-4 py-3 rounded-lg border border-gray-200 text-sm text-gray-900 placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-brand-blue/30 focus:border-brand-blue transition-all"
      />

      {/* Platforms */}
      <div className="mt-4">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Plataformas</label>
        <div className="flex flex-wrap gap-2 mt-2">
          {ALL_PLATFORMS.map(p => (
            <button
              key={p.id}
              onClick={() => togglePlatform(p.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                platforms.includes(p.id)
                  ? 'bg-brand-blue text-white shadow-sm'
                  : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
              }`}
            >
              {p.emoji} {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Languages */}
      <div className="mt-4">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Idiomas</label>
        <div className="flex gap-2 mt-2">
          {LANGUAGES.map(l => (
            <button
              key={l.id}
              onClick={() => toggleLanguage(l.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                languages.includes(l.id)
                  ? 'bg-brand-purple text-white shadow-sm'
                  : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mt-3 text-xs text-red-600 bg-red-50 px-3 py-2 rounded-lg">
          {error}
        </div>
      )}

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={!brief.trim() || platforms.length === 0 || languages.length === 0 || submitting}
        className="mt-5 w-full flex items-center justify-center gap-2 px-6 py-3 bg-brand-gradient text-white font-semibold rounded-lg shadow-sm hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {submitting ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Rocket className="w-4 h-4" />
        )}
        {submitting ? 'Lanzando...' : 'Lanzar Campaña'}
      </button>
    </div>
  )
}
