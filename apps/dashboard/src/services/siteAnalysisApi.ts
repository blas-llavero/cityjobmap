import { API_BASE_URL } from './apiConfig'

export type SiteAnalysisStatus =
  | 'specific_job_match'
  | 'possible_active_offer'
  | 'careers_page'
  | 'contact_page'
  | 'website_only'
  | 'robots_blocked'

export type SiteEvidence = {
  kind: 'job_match' | 'offer' | 'careers' | 'contact'
  label: string
  url: string
  excerpt: string | null
}

export type SiteAnalysis = {
  website: string
  final_home_url: string
  status: SiteAnalysisStatus
  status_label: string
  career_url: string | null
  contact_url: string | null
  job_query?: string | null
  job_match_url?: string | null
  pages_checked: string[]
  evidence: SiteEvidence[]
  blocked_urls: string[]
  detected_language?: string | null
  analysis_languages?: string[]
}

type ApiErrorResponse = {
  detail?: string
}


export async function analyzeWebsite(
  website: string,
  languages: string[],
  jobQuery = '',
  signal?: AbortSignal,
): Promise<SiteAnalysis> {
  const response = await fetch(`${API_BASE_URL}/analyze-site`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      website,
      languages,
      job_query: jobQuery.trim() || null,
    }),
    signal,
  })

  if (!response.ok) {
    let message = `L’API ha retornat l’error ${response.status}.`

    try {
      const errorData = (await response.json()) as ApiErrorResponse

      if (errorData.detail) {
        message = errorData.detail
      }
    } catch {
      // Conserva el missatge genèric.
    }

    throw new Error(message)
  }

  return (await response.json()) as SiteAnalysis
}
