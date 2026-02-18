/**
 * Data layer for the dashboard.
 * In production (Vercel): fetches from the backend API on the VPS.
 * In development: fetches from the backend API or reads local files as fallback.
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000'

// --- Types ---

export interface AgentResult {
  agent: string
  status: 'completed' | 'error'
  result_length?: number
  error?: string
}

export interface PipelineState {
  phases?: Record<string, { name: string; results: AgentResult[] }>
  errors?: AgentResult[]
  status?: string
  phase?: number
  phase_name?: string
  campaign_brief?: string
  agents_completed?: string[]
}

export interface TrendItem {
  topic: string
  relevance_score?: number
  engagement_level?: string
  platform?: string
  description?: string
}

export interface PlatformTrend {
  platform: string
  trends: TrendItem[]
}

export interface TrendReport {
  generation_date?: string
  platform_trends?: PlatformTrend[]
  top_global_trends?: TrendItem[]
  recommended_topics?: string[]
  nicho_relevance_summary?: string
}

export interface ContentSlot {
  slot_id: string
  platform: string
  content_type: string
  topic: string
  hook_idea?: string
  viral_pattern?: string
  language: string
  pillar?: string
  scheduled_time?: string
  priority?: string
}

export interface DayPlan {
  date: string
  content_slots: ContentSlot[]
}

export interface ContentPlan {
  week_start?: string
  week_end?: string
  total_posts?: number
  daily_plans?: DayPlan[]
  pillar_distribution?: Record<string, number>
  platform_distribution?: Record<string, number>
}

export interface Script {
  slot_id: string
  platform: string
  content_type: string
  language: string
  hook?: string
  script_body?: string
  cta?: string
  caption?: string
  visual_notes?: string
  word_count?: number
  estimated_duration_seconds?: number
}

export interface ContentScripts {
  scripts: Script[]
  total_scripts?: number
}

export interface ContentReview {
  slot_id: string
  voice_score?: number
  message_consistency_score?: number
  reputation_risk_score?: number
  quality_score?: number
  overall_score?: number
  status?: string
  issues?: string[]
  suggestions?: string[]
}

export interface BrandComplianceReport {
  batch_score?: number
  batch_recommendation?: string
  content_reviews?: ContentReview[]
  critical_issues?: string[]
  summary?: string
}

export interface PlatformSummary {
  platform: string
  posts?: number
  avg_engagement?: number
  total_reach?: number
  total_views?: number
  total_impressions?: number
}

export interface EngagementReport {
  period?: string
  overall_engagement_rate?: number
  platform_summary?: Record<string, PlatformSummary>
  top_performers?: any[]
  bottom_performers?: any[]
  pillar_performance?: Record<string, any>
  insights?: string[]
  recommendations_next_cycle?: string[]
}

export interface ApprovalDecision {
  id: string
  checkpoint: 'post_planning' | 'post_production' | 'pre_publication'
  item_id: string
  status: 'approved' | 'rejected' | 'needs_revision'
  feedback: string
  timestamp: string
}

export interface ApprovalsFile {
  decisions: ApprovalDecision[]
}

// --- API Client ---

async function fetchBackend<T>(endpoint: string, options?: RequestInit): Promise<T | null> {
  try {
    const res = await fetch(`${BACKEND_URL}${endpoint}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      cache: 'no-store',
    })
    if (!res.ok) return null
    return await res.json()
  } catch {
    return null
  }
}

// --- Public API (used by server components) ---

export function getBackendUrl(): string {
  return BACKEND_URL
}

export async function getPipelineState(): Promise<PipelineState> {
  const data = await fetchBackend<{ pipeline: PipelineState }>('/api/pipeline')
  return data?.pipeline || { status: 'idle', phase: 0 }
}

export async function getTrendReport(): Promise<TrendReport | null> {
  const data = await fetchBackend<{ data: TrendReport }>('/api/content/trends')
  return data?.data || null
}

export async function getContentPlan(): Promise<ContentPlan | null> {
  const data = await fetchBackend<{ data: ContentPlan }>('/api/content/plan')
  return data?.data || null
}

export async function getContentScripts(): Promise<ContentScripts | null> {
  const data = await fetchBackend<{ data: ContentScripts }>('/api/content/scripts')
  return data?.data || null
}

export async function getBrandCompliance(): Promise<BrandComplianceReport | null> {
  const data = await fetchBackend<{ data: BrandComplianceReport }>('/api/content/compliance')
  return data?.data || null
}

export async function getEngagementReport(): Promise<EngagementReport | null> {
  const data = await fetchBackend<{ data: EngagementReport }>('/api/content/engagement')
  return data?.data || null
}

export async function getApprovals(): Promise<ApprovalsFile> {
  const data = await fetchBackend<ApprovalsFile>('/api/approvals')
  return data || { decisions: [] }
}
