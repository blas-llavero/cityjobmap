import { useMemo, useRef, useState } from 'react'
import './App.css'
import { analyzeWebsite } from './services/siteAnalysisApi'
import type { SiteAnalysis } from './services/siteAnalysisApi'
import {
  geocodeLocation,
  reverseGeocodeLocation,
} from './services/locationApi'
import type { GeocodedLocation } from './services/locationApi'
import { evaluateOrganization } from './services/matching'
import type { OrganizationEvaluation } from './services/matching'
import { searchOrganizations } from './services/overpass'
import type { OrganizationResult } from './services/overpass'
import { LocationMap } from './components/LocationMap'

type Profession = {
  id: string
  label: string
  description: string
}

type EvaluatedOrganization = {
  organization: OrganizationResult
  evaluation: OrganizationEvaluation
}

type SearchLanguageCode =
  | 'en'
  | 'de'
  | 'fr'
  | 'it'
  | 'ca'
  | 'es'

type SearchLanguage = {
  code: SearchLanguageCode
  label: string
  nativeLabel: string
}

const SEARCH_LANGUAGES: SearchLanguage[] = [
  {
    code: 'en',
    label: 'Anglès',
    nativeLabel: 'English',
  },
  {
    code: 'de',
    label: 'Alemany',
    nativeLabel: 'Deutsch',
  },
  {
    code: 'fr',
    label: 'Francès',
    nativeLabel: 'Français',
  },
  {
    code: 'it',
    label: 'Italià',
    nativeLabel: 'Italiano',
  },
  {
    code: 'ca',
    label: 'Català',
    nativeLabel: 'Català',
  },
  {
    code: 'es',
    label: 'Castellà',
    nativeLabel: 'Español',
  },
]

const PROFESSIONS: Profession[] = [
  {
    id: 'bioinformatics',
    label: 'Bioinformàtica',
    description:
      'Bioinformàtic, bioinformatics i perfils computacionals biomèdics',
  },
  {
    id: 'it',
    label: 'Informàtica',
    description: 'Tècnic informàtic, suport, sistemes, xarxes i programació',
  },
  {
    id: 'cybersecurity',
    label: 'Ciberseguretat',
    description: 'Seguretat informàtica, SOC, xarxes i administració segura',
  },
  {
    id: 'math-teacher',
    label: 'Professor/a de matemàtiques',
    description: 'ESO, batxillerat, formació professional i acadèmies',
  },
  {
    id: 'computer-teacher',
    label: "Professor/a d'informàtica",
    description:
      'Programació, sistemes, xarxes, ciberseguretat i formació digital',
  },
  {
    id: 'technology-teacher',
    label: 'Professor/a de tecnologia',
    description: 'Tecnologia, robòtica, fabricació digital i projectes STEM',
  },
  {
    id: 'electricity-teacher',
    label: "Professor/a d'electricitat",
    description:
      'Instal·lacions elèctriques, automatització i formació professional',
  },
  {
    id: 'electronics-teacher',
    label: "Professor/a d'electrònica",
    description: 'Electrònica, sistemes digitals, IoT i automatització',
  },
]

function getRelevanceLabel(
  evaluation: OrganizationEvaluation,
): string {
  if (evaluation.level === 'high') {
    return 'Rellevància alta'
  }

  if (evaluation.level === 'medium') {
    return 'Rellevància mitjana'
  }

  return 'Poc relacionada'
}


type OpportunityTone =
  | 'match'
  | 'offer'
  | 'careers'
  | 'contact'
  | 'none'
  | 'blocked'

type OpportunityView = {
  title: string
  description: string
  primaryUrl: string | null
  primaryLabel: string | null
  tone: OpportunityTone
}

function buildOpportunityView(
  analysis: SiteAnalysis,
): OpportunityView {
  if (analysis.status === 'specific_job_match') {
    const jobEvidence = analysis.evidence.find(
      (item) => item.kind === 'job_match',
    )

    return {
      title: 'Coincidència específica amb la professió',
      description:
        analysis.job_query
          ? `S’ha trobat «${analysis.job_query}» dins d’una pàgina laboral o d’una possible oferta.`
          : 'S’ha trobat la professió cercada dins d’una pàgina laboral o d’una possible oferta.',
      primaryUrl:
        jobEvidence?.url ??
        analysis.job_match_url ??
        analysis.career_url ??
        analysis.final_home_url,
      primaryLabel: 'Revisa la coincidència',
      tone: 'match',
    }
  }

  if (analysis.status === 'possible_active_offer') {
    const offerEvidence = analysis.evidence.find(
      (item) => item.kind === 'offer',
    )

    return {
      title: 'Possible oferta activa detectada',
      description:
        'S’ha trobat text compatible amb una oferta. Cal revisar-lo manualment abans de considerar-la activa.',
      primaryUrl:
        offerEvidence?.url ??
        analysis.career_url ??
        analysis.final_home_url,
      primaryLabel: 'Revisa l’oferta',
      tone: 'offer',
    }
  }

  if (analysis.status === 'careers_page') {
    return {
      title: 'Pàgina «Treballa amb nosaltres» detectada',
      description:
        'La web disposa d’una secció dedicada a feina, vacants o incorporació de personal.',
      primaryUrl:
        analysis.career_url ??
        analysis.final_home_url,
      primaryLabel: 'Obre Treballa amb nosaltres',
      tone: 'careers',
    }
  }

  if (analysis.status === 'contact_page') {
    return {
      title: 'Contacte per candidatura espontània',
      description:
        'No s’ha detectat cap oferta activa, però pots revisar el contacte oficial de l’organització.',
      primaryUrl:
        analysis.contact_url ??
        analysis.final_home_url,
      primaryLabel: 'Obre el contacte',
      tone: 'contact',
    }
  }

  if (analysis.status === 'robots_blocked') {
    return {
      title: 'Anàlisi bloquejada per robots.txt',
      description:
        'La web no permet aquesta exploració automàtica. Pots revisar-la manualment.',
      primaryUrl: analysis.final_home_url,
      primaryLabel: 'Obre la web manualment',
      tone: 'blocked',
    }
  }

  return {
    title: 'Cap oportunitat laboral localitzada',
    description:
      'No s’ha localitzat cap oferta, secció laboral ni contacte específic durant aquesta anàlisi.',
    primaryUrl: analysis.final_home_url,
    primaryLabel: 'Obre la web',
    tone: 'none',
  }
}

function formatAnalysisLanguage(
  languageCode: string,
): string {
  const language = SEARCH_LANGUAGES.find(
    (item) => item.code === languageCode,
  )

  if (!language) {
    return languageCode.toUpperCase()
  }

  return `${language.nativeLabel} · ${language.code.toUpperCase()}`
}

function SiteOpportunityCard({
  analysis,
}: {
  analysis: SiteAnalysis
}) {
  const view = buildOpportunityView(analysis)

  const evidenceWithExcerpt = analysis.evidence.find(
    (item) => item.excerpt,
  )

  const secondaryContactUrl =
    analysis.contact_url &&
    analysis.contact_url !== view.primaryUrl
      ? analysis.contact_url
      : null

  return (
    <div
      className={`opportunity-card opportunity-${view.tone}`}
    >
      <div className="opportunity-heading">
        <span className="opportunity-indicator" aria-hidden="true" />

        <strong>{view.title}</strong>
      </div>

      <p>{view.description}</p>

      <div className="detected-language-panel">
        {analysis.detected_language ? (
          <span>
            Idioma detectat:{' '}
            <strong>
              {formatAnalysisLanguage(
                analysis.detected_language,
              )}
            </strong>
          </span>
        ) : (
          <span>
            Idioma declarat: no detectat
          </span>
        )}

        {(analysis.analysis_languages?.length ?? 0) > 0 && (
          <small>
            Idiomes aplicats:{' '}
            {analysis.analysis_languages
              ?.map(formatAnalysisLanguage)
              .join(' · ')}
          </small>
        )}
      </div>

      <div className="opportunity-actions">
        {view.primaryUrl && view.primaryLabel && (
          <a
            className="opportunity-primary-link"
            href={view.primaryUrl}
            target="_blank"
            rel="noreferrer"
          >
            {view.primaryLabel}
          </a>
        )}

        {secondaryContactUrl && (
          <a
            className="opportunity-secondary-link"
            href={secondaryContactUrl}
            target="_blank"
            rel="noreferrer"
          >
            Obre també el contacte
          </a>
        )}
      </div>

      {evidenceWithExcerpt?.excerpt && (
        <small className="opportunity-evidence">
          Evidència: {evidenceWithExcerpt.excerpt}
        </small>
      )}

      <small className="pages-checked">
        {analysis.pages_checked.length} pàgines revisades
      </small>
    </div>
  )
}



const BATCH_DELAY_MS = 1500

const SITE_ANALYSIS_PRIORITY: Record<
  SiteAnalysis['status'],
  number
> = {
  specific_job_match: 0,
  possible_active_offer: 1,
  careers_page: 2,
  contact_page: 3,
  website_only: 4,
  robots_blocked: 5,
}

function waitForMilliseconds(
  milliseconds: number,
  signal: AbortSignal,
): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal.aborted) {
      reject(
        new DOMException(
          'Operació cancel·lada',
          'AbortError',
        ),
      )
      return
    }

    const handleAbort = () => {
      window.clearTimeout(timerId)

      reject(
        new DOMException(
          'Operació cancel·lada',
          'AbortError',
        ),
      )
    }

    const timerId = window.setTimeout(() => {
      signal.removeEventListener('abort', handleAbort)
      resolve()
    }, milliseconds)

    signal.addEventListener('abort', handleAbort, {
      once: true,
    })
  })
}

async function waitWhileBatchIsPaused(
  signal: AbortSignal,
  isPaused: () => boolean,
): Promise<void> {
  while (isPaused()) {
    await waitForMilliseconds(250, signal)
  }
}


function App() {
  const [selectedProfessionIds, setSelectedProfessionIds] = useState<string[]>([
    'bioinformatics',
    'it',
    'computer-teacher',
  ])

  const [customJobQuery, setCustomJobQuery] =
    useState('')

  const [selectedLanguageCodes, setSelectedLanguageCodes] =
    useState<SearchLanguageCode[]>(['en'])

  const [locationQuery, setLocationQuery] =
    useState('')

  const [resolvedLocation, setResolvedLocation] =
    useState<GeocodedLocation | null>(null)

  const [isLocating, setIsLocating] = useState(false)
  const [locationError, setLocationError] =
    useState<string | null>(null)

  const [radiusKm, setRadiusKm] = useState(0)
  const [searchPrepared, setSearchPrepared] = useState(false)
  const [organizations, setOrganizations] = useState<OrganizationResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [showLowRelevance, setShowLowRelevance] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [siteAnalyses, setSiteAnalyses] = useState<
    Record<string, SiteAnalysis>
  >({})
  const [siteAnalysisErrors, setSiteAnalysisErrors] = useState<
    Record<string, string>
  >({})
  const [analyzingOrganizationId, setAnalyzingOrganizationId] = useState<
    string | null
  >(null)
  const [isBatchAnalyzing, setIsBatchAnalyzing] = useState(false)
  const [isBatchPaused, setIsBatchPaused] = useState(false)
  const [batchProgress, setBatchProgress] = useState({
    completed: 0,
    total: 0,
  })

  const [
    batchQueuedOrganizationIds,
    setBatchQueuedOrganizationIds,
  ] = useState<string[]>([])

  const [notice, setNotice] = useState(
    'Selecciona els perfils professionals que vols cercar.',
  )

  const mapSelectionIdRef = useRef(0)
  const reverseGeocodeTimerRef =
    useRef<number | null>(null)

  const searchControllerRef = useRef<AbortController | null>(null)
  const batchControllerRef = useRef<AbortController | null>(null)
  const batchPausedRef = useRef(false)

  const selectedProfessions = useMemo(
    () =>
      PROFESSIONS.filter((profession) =>
        selectedProfessionIds.includes(profession.id),
      ),
    [selectedProfessionIds],
  )

  const evaluatedOrganizations = useMemo<EvaluatedOrganization[]>(() => {
    return organizations
      .map((organization) => ({
        organization,
        evaluation: evaluateOrganization(
          organization,
          selectedProfessionIds,
          selectedLanguageCodes,
          customJobQuery,
        ),
      }))
      .sort((first, second) => {
        if (first.evaluation.score !== second.evaluation.score) {
          return second.evaluation.score - first.evaluation.score
        }

        const firstDistance =
          first.organization.distanceKm ?? Number.POSITIVE_INFINITY

        const secondDistance =
          second.organization.distanceKm ?? Number.POSITIVE_INFINITY

        if (firstDistance !== secondDistance) {
          return firstDistance - secondDistance
        }

        return first.organization.name.localeCompare(
          second.organization.name,
          'ca',
        )
      })
  }, [
    organizations,
    selectedProfessionIds,
    selectedLanguageCodes,
    customJobQuery,
  ])

  const relevantOrganizations = useMemo(
    () => {
      const hasCustomJobQuery =
        customJobQuery.trim().length >= 2

      if (
        hasCustomJobQuery &&
        selectedProfessionIds.length === 0
      ) {
        return evaluatedOrganizations
      }

      return evaluatedOrganizations.filter(
        ({ evaluation }) => evaluation.isRelevant,
      )
    },
    [
      evaluatedOrganizations,
      customJobQuery,
      selectedProfessionIds.length,
    ],
  )

  const visibleOrganizations = useMemo(() => {
    const baseOrganizations = showLowRelevance
      ? evaluatedOrganizations
      : relevantOrganizations

    /*
     * Durant una anàlisi per lots mantenim exactament
     * l'ordre que ja tenien els resultats.
     *
     * Això evita que les files saltin de posició cada
     * vegada que acaba l'anàlisi d'una empresa.
     */
    if (isBatchAnalyzing) {
      return [...baseOrganizations]
    }

    return [...baseOrganizations].sort((first, second) => {
      const firstAnalysis =
        siteAnalyses[first.organization.id]

      const secondAnalysis =
        siteAnalyses[second.organization.id]

      const firstPriority = firstAnalysis
        ? SITE_ANALYSIS_PRIORITY[firstAnalysis.status]
        : 5

      const secondPriority = secondAnalysis
        ? SITE_ANALYSIS_PRIORITY[secondAnalysis.status]
        : 5

      if (firstPriority !== secondPriority) {
        return firstPriority - secondPriority
      }

      if (first.evaluation.score !== second.evaluation.score) {
        return second.evaluation.score - first.evaluation.score
      }

      const firstDistance =
        first.organization.distanceKm ??
        Number.POSITIVE_INFINITY

      const secondDistance =
        second.organization.distanceKm ??
        Number.POSITIVE_INFINITY

      return firstDistance - secondDistance
    })
  }, [
    evaluatedOrganizations,
    relevantOrganizations,
    showLowRelevance,
    siteAnalyses,
    isBatchAnalyzing,
  ])

  const unanalyzedVisibleWebsiteCount = useMemo(
    () =>
      visibleOrganizations.filter(
        ({ organization }) =>
          organization.website &&
          !siteAnalyses[organization.id],
      ).length,
    [visibleOrganizations, siteAnalyses],
  )

  const hiddenLowRelevanceCount =
    evaluatedOrganizations.length - relevantOrganizations.length

  const clearCurrentSearch = () => {
    searchControllerRef.current?.abort()
    searchControllerRef.current = null

    setSearchPrepared(false)
    setRadiusKm(0)
    setOrganizations([])
    setShowLowRelevance(false)
    setErrorMessage(null)
    batchControllerRef.current?.abort()
    batchControllerRef.current = null
    batchPausedRef.current = false

    setSiteAnalyses({})
    setSiteAnalysisErrors({})
    setAnalyzingOrganizationId(null)
    setIsBatchAnalyzing(false)
    setIsBatchPaused(false)
    setBatchProgress({
      completed: 0,
      total: 0,
    })

    setBatchQueuedOrganizationIds([])
  }

  const handleLocationQueryChange = (
    value: string,
  ) => {
    mapSelectionIdRef.current += 1

    if (reverseGeocodeTimerRef.current !== null) {
      window.clearTimeout(
        reverseGeocodeTimerRef.current,
      )

      reverseGeocodeTimerRef.current = null
    }

    setLocationQuery(value)
    setResolvedLocation(null)
    setLocationError(null)

    clearCurrentSearch()

    setNotice(
      'La ubicació ha canviat. Prem «Localitza» abans de començar la cerca.',
    )
  }

  const locateSearchLocation = async () => {
    const query = locationQuery.trim()

    if (query.length < 2) {
      setLocationError(
        'Escriu una ciutat o ubicació vàlida.',
      )
      return
    }

    setIsLocating(true)
    setLocationError(null)

    setNotice(
      `Localitzant «${query}»...`,
    )

    try {
      const location = await geocodeLocation(query)

      setResolvedLocation(location)

      setNotice(
        `Ubicació localitzada: ${location.location_name} (${location.country_code.toUpperCase()}).`,
      )
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : 'No s’ha pogut localitzar aquesta ubicació.'

      setResolvedLocation(null)
      setLocationError(message)

      setNotice(
        'No s’ha pogut validar la ubicació.',
      )
    } finally {
      setIsLocating(false)
    }
  }

  const selectLocationFromMap = (
    latitude: number,
    longitude: number,
  ) => {
    const selectionId =
      mapSelectionIdRef.current + 1

    mapSelectionIdRef.current = selectionId

    if (reverseGeocodeTimerRef.current !== null) {
      window.clearTimeout(
        reverseGeocodeTimerRef.current,
      )
    }

    const coordinateLabel =
      `${latitude.toFixed(5)}, ${longitude.toFixed(5)}`

    clearCurrentSearch()

    setLocationQuery('')
    setLocationError(null)

    setResolvedLocation({
      query: coordinateLabel,
      display_name:
        `Punt seleccionat al mapa (${coordinateLabel})`,
      latitude,
      longitude,
      country_code: '',
      location_name: 'Punt del mapa',
      bounding_box: null,
    })

    setNotice(
      `Punt seleccionat: ${coordinateLabel}. ` +
      'Identificant la ubicació...',
    )

    reverseGeocodeTimerRef.current =
      window.setTimeout(() => {
        reverseGeocodeTimerRef.current = null

        void reverseGeocodeLocation(
          latitude,
          longitude,
        )
          .then((location) => {
            if (
              selectionId !==
              mapSelectionIdRef.current
            ) {
              return
            }

            setResolvedLocation(location)

            const country =
              location.country_code
                ? ` (${location.country_code.toUpperCase()})`
                : ''

            setNotice(
              `Ubicació identificada: ` +
              `${location.location_name}${country}.`,
            )
          })
          .catch(() => {
            if (
              selectionId !==
              mapSelectionIdRef.current
            ) {
              return
            }

            setNotice(
              `Punt seleccionat: ${coordinateLabel}. ` +
              'No s’ha pogut identificar el municipi, ' +
              'però pots cercar igualment.',
            )
          })
      }, 1100)
  }

  const toggleSearchLanguage = (
    languageCode: SearchLanguageCode,
  ) => {
    setSelectedLanguageCodes((currentCodes) =>
      currentCodes.includes(languageCode)
        ? currentCodes.filter(
            (code) => code !== languageCode,
          )
        : [...currentCodes, languageCode],
    )

    setNotice(
      'Idiomes de cerca actualitzats. Al pas 12B els connectarem amb l’anàlisi de les webs.',
    )
  }

  const selectAllSearchLanguages = () => {
    setSelectedLanguageCodes(
      SEARCH_LANGUAGES.map(
        (language) => language.code,
      ),
    )

    setNotice(
      'S’han seleccionat tots els idiomes de cerca.',
    )
  }

  const clearSearchLanguages = () => {
    setSelectedLanguageCodes([])

    setNotice(
      'No hi ha cap idioma seleccionat. Selecciona com a mínim un idioma abans de l’anàlisi web.',
    )
  }

  const toggleProfession = (professionId: string) => {
    clearCurrentSearch()

    setSelectedProfessionIds((currentIds) =>
      currentIds.includes(professionId)
        ? currentIds.filter((id) => id !== professionId)
        : [...currentIds, professionId],
    )

    setNotice(
      'La selecció ha canviat. Prepara una nova cerca per actualitzar els resultats.',
    )
  }

  const selectAllProfessions = () => {
    clearCurrentSearch()
    setSelectedProfessionIds(PROFESSIONS.map((profession) => profession.id))
    setNotice('S’han seleccionat tots els perfils professionals.')
  }

  const clearProfessions = () => {
    clearCurrentSearch()
    setSelectedProfessionIds([])
    setNotice('Selecciona com a mínim un perfil professional.')
  }

  const runSearch = async (
    targetRadiusKm: number,
    replaceExistingResults: boolean,
  ): Promise<boolean> => {
    searchControllerRef.current?.abort()

    const controller = new AbortController()
    searchControllerRef.current = controller

    setIsSearching(true)
    setErrorMessage(null)

    const searchLocationName =
      resolvedLocation?.location_name ??
      'la ubicació seleccionada'

    setNotice(
      targetRadiusKm === 0
        ? `Cercant i classificant organitzacions a ${searchLocationName}...`
        : `Cercant i classificant organitzacions fins a ${targetRadiusKm} km de ${searchLocationName}...`,
    )

    try {
      if (!resolvedLocation) {
        throw new Error(
          'No hi ha cap ubicació seleccionada.',
        )
      }

      const foundOrganizations =
        await searchOrganizations(
          resolvedLocation,
          targetRadiusKm,
          controller.signal,
        )

      setOrganizations((currentOrganizations) => {
        const mergedOrganizations = new Map<string, OrganizationResult>()

        if (!replaceExistingResults) {
          for (const organization of currentOrganizations) {
            mergedOrganizations.set(organization.id, organization)
          }
        }

        for (const organization of foundOrganizations) {
          mergedOrganizations.set(organization.id, organization)
        }

        return [...mergedOrganizations.values()]
      })

      setNotice(
        targetRadiusKm === 0
          ? `Cerca completada a ${searchLocationName}: ${foundOrganizations.length} organitzacions analitzades.`
          : `Cerca completada fins a ${targetRadiusKm} km de ${searchLocationName}: ${foundOrganizations.length} organitzacions analitzades dins del radi.`,
      )

      return true
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        return false
      }

      const message =
        error instanceof Error
          ? error.message
          : 'S’ha produït un error desconegut.'

      setErrorMessage(message)
      setNotice('No s’ha pogut completar la consulta a OpenStreetMap.')

      return false
    } finally {
      if (searchControllerRef.current === controller) {
        searchControllerRef.current = null
        setIsSearching(false)
      }
    }
  }

  const prepareSearch = async () => {
    if (!resolvedLocation) {
      setNotice(
        'Primer has de localitzar una ubicació vàlida.',
      )
      return
    }

    if (
      selectedProfessionIds.length === 0 &&
      customJobQuery.trim().length < 2
    ) {
      setNotice(
        'Selecciona un perfil professional o escriu una professió a la cerca lliure.',
      )
      return
    }

    setRadiusKm(0)
    setSearchPrepared(false)
    setOrganizations([])
    setShowLowRelevance(false)

    const successful = await runSearch(0, true)
    setSearchPrepared(successful)
  }

  const expandSearch = async () => {
    if (!searchPrepared) {
      setNotice('Primer has de completar la cerca inicial a la ubicació seleccionada.')
      return
    }

    const nextRadiusKm = radiusKm + 20
    const successful = await runSearch(nextRadiusKm, false)

    if (successful) {
      setRadiusKm(nextRadiusKm)
    }
  }

  const resetSearch = () => {
    clearCurrentSearch()

    setNotice(
      'La cerca s’ha reiniciat. Pots modificar els perfils i començar de nou.',
    )
  }

  const analyzeOrganizationWebsite = async (
    organization: OrganizationResult,
  ) => {
    if (selectedLanguageCodes.length === 0) {
      setNotice(
        'Selecciona com a mínim un idioma de cerca abans d’analitzar la web.',
      )
      return
    }

    if (!organization.website || isBatchAnalyzing) {
      return
    }

    setAnalyzingOrganizationId(organization.id)

    setSiteAnalysisErrors((currentErrors) => {
      const nextErrors = { ...currentErrors }
      delete nextErrors[organization.id]
      return nextErrors
    })

    try {
      const analysis = await analyzeWebsite(
        organization.website,
        selectedLanguageCodes,
        customJobQuery,
      )

      setSiteAnalyses((currentAnalyses) => ({
        ...currentAnalyses,
        [organization.id]: analysis,
      }))
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : 'No s’ha pogut analitzar la web.'

      setSiteAnalysisErrors((currentErrors) => ({
        ...currentErrors,
        [organization.id]: message,
      }))
    } finally {
      setAnalyzingOrganizationId((currentId) =>
        currentId === organization.id ? null : currentId,
      )
    }
  }

  const analyzeVisibleWebsites = async () => {
    if (isBatchAnalyzing) {
      return
    }

    if (selectedLanguageCodes.length === 0) {
      setNotice(
        'Selecciona com a mínim un idioma de cerca abans d’analitzar les webs.',
      )
      return
    }

    const candidates = visibleOrganizations
      .map(({ organization }) => organization)
      .filter(
        (organization) =>
          organization.website &&
          !siteAnalyses[organization.id],
      )

    if (candidates.length === 0) {
      setNotice(
        'No queden webs visibles pendents d’analitzar.',
      )
      return
    }

    const controller = new AbortController()
    batchControllerRef.current = controller
    batchPausedRef.current = false

    setIsBatchAnalyzing(true)
    setIsBatchPaused(false)
    setBatchProgress({
      completed: 0,
      total: candidates.length,
    })

    setBatchQueuedOrganizationIds(
      candidates.map(
        (organization) => organization.id,
      ),
    )

    setNotice(
      `Comença l’anàlisi automàtica de ${candidates.length} webs.`,
    )

    let completed = 0

    try {
      for (
        let index = 0;
        index < candidates.length;
        index += 1
      ) {
        const organization = candidates[index]

        await waitWhileBatchIsPaused(
          controller.signal,
          () => batchPausedRef.current,
        )

        if (!organization.website) {
          continue
        }

        setAnalyzingOrganizationId(organization.id)

        setSiteAnalysisErrors((currentErrors) => {
          const nextErrors = { ...currentErrors }
          delete nextErrors[organization.id]
          return nextErrors
        })

        try {
          const analysis = await analyzeWebsite(
            organization.website,
            selectedLanguageCodes,
            customJobQuery,
            controller.signal,
          )

          setSiteAnalyses((currentAnalyses) => ({
            ...currentAnalyses,
            [organization.id]: analysis,
          }))
        } catch (error) {
          if (
            error instanceof Error &&
            error.name === 'AbortError'
          ) {
            throw error
          }

          const message =
            error instanceof Error
              ? error.message
              : 'No s’ha pogut analitzar la web.'

          setSiteAnalysisErrors((currentErrors) => ({
            ...currentErrors,
            [organization.id]: message,
          }))
        } finally {
          completed = index + 1

          setBatchProgress({
            completed,
            total: candidates.length,
          })

          setAnalyzingOrganizationId((currentId) =>
            currentId === organization.id
              ? null
              : currentId,
          )

          setBatchQueuedOrganizationIds(
            (currentIds) =>
              currentIds.filter(
                (organizationId) =>
                  organizationId !==
                  organization.id,
              ),
          )
        }

        if (index < candidates.length - 1) {
          await waitForMilliseconds(
            BATCH_DELAY_MS,
            controller.signal,
          )
        }
      }

      setNotice(
        `Anàlisi automàtica completada: ${completed} webs processades.`,
      )
    } catch (error) {
      if (
        error instanceof Error &&
        error.name === 'AbortError'
      ) {
        setNotice(
          `Anàlisi automàtica aturada després de ${completed} webs.`,
        )
      } else {
        const message =
          error instanceof Error
            ? error.message
            : 'Error durant l’anàlisi automàtica.'

        setErrorMessage(message)
        setNotice(
          'L’anàlisi automàtica s’ha interromput.',
        )
      }
    } finally {
      if (batchControllerRef.current === controller) {
        batchControllerRef.current = null
      }

      batchPausedRef.current = false
      setIsBatchAnalyzing(false)
      setIsBatchPaused(false)
      setAnalyzingOrganizationId(null)
    }
  }

  const toggleBatchPause = () => {
    const nextPausedState = !batchPausedRef.current

    batchPausedRef.current = nextPausedState
    setIsBatchPaused(nextPausedState)

    setNotice(
      nextPausedState
        ? 'Anàlisi automàtica en pausa. La pausa s’aplicarà després de la web actual.'
        : 'Anàlisi automàtica represa.',
    )
  }

  const stopBatchAnalysis = () => {
    setNotice('Aturant l’anàlisi automàtica...')
    batchControllerRef.current?.abort()
  }

  const selectedLocationName =
    resolvedLocation?.location_name ?? 'Ubicació pendent'

  const currentArea =
    radiusKm === 0
      ? selectedLocationName
      : `Fins a ${radiusKm} km de ${selectedLocationName}`

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">
            RT
          </div>

          <div>
            <p className="brand-kicker">Cerca laboral territorial</p>
            <h1>CityJobMap</h1>
          </div>
        </div>

        <div className="topbar-status">
          <span className="status-dot" aria-hidden="true" />
          Aplicació local
        </div>
      </header>

      <main className="dashboard">
        <aside className="search-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Configuració</p>
              <h2>Nova cerca</h2>
            </div>

            <span className="step-badge">1</span>
          </div>

          <label className="field-label" htmlFor="base-location">
            Ubicació inicial
          </label>

          <div className="location-search-row">
            <div className="location-field">
              <span aria-hidden="true">⌖</span>

              <input
                id="base-location"
                type="text"
                value={locationQuery}
                disabled={
                  isSearching ||
                  isBatchAnalyzing ||
                  isLocating
                }
                onChange={(event) =>
                  handleLocationQueryChange(
                    event.target.value,
                  )
                }
                onKeyDown={(event) => {
                  if (event.key === 'Enter') {
                    event.preventDefault()
                    void locateSearchLocation()
                  }
                }}
                placeholder="Ex.: Zürich, Switzerland"
              />
            </div>

            <button
              className="locate-button"
              type="button"
              disabled={
                isLocating ||
                isSearching ||
                isBatchAnalyzing ||
                locationQuery.trim().length < 2
              }
              onClick={() =>
                void locateSearchLocation()
              }
            >
              {isLocating ? 'Localitzant...' : 'Localitza'}
            </button>
          </div>

          <div
            className="location-map-separator"
            aria-hidden="true"
          >
            <span>o selecciona un punt al mapa</span>
          </div>

          <LocationMap
            latitude={resolvedLocation?.latitude}
            longitude={resolvedLocation?.longitude}
            onSelect={selectLocationFromMap}
          />

          {resolvedLocation && (
            <div className="resolved-location-card">
              <span
                className="resolved-location-check"
                aria-hidden="true"
              >
                ✓
              </span>

              <div>
                <strong>
                  {resolvedLocation.location_name}
                  {resolvedLocation.country_code && (
                    <>
                      {' · '}
                      {resolvedLocation.country_code.toUpperCase()}
                    </>
                  )}
                </strong>

                <small>
                  {resolvedLocation.display_name}
                </small>

                <small>
                  {resolvedLocation.latitude.toFixed(5)}
                  {', '}
                  {resolvedLocation.longitude.toFixed(5)}
                </small>
              </div>
            </div>
          )}

          {locationError && (
            <div
              className="location-error"
              role="alert"
            >
              {locationError}
            </div>
          )}


          <section className="language-section">
            <div className="section-title-row">
              <div>
                <p className="field-label">
                  Idiomes de cerca
                </p>

                <p className="field-help">
                  {selectedLanguageCodes.length} seleccionats
                </p>
              </div>

              <div className="small-actions">
                <button
                  type="button"
                  disabled={
                    isSearching ||
                    isBatchAnalyzing
                  }
                  onClick={selectAllSearchLanguages}
                >
                  Tots
                </button>

                <button
                  type="button"
                  disabled={
                    isSearching ||
                    isBatchAnalyzing
                  }
                  onClick={clearSearchLanguages}
                >
                  Neteja
                </button>
              </div>
            </div>

            <div className="language-grid">
              {SEARCH_LANGUAGES.map((language) => {
                const checked =
                  selectedLanguageCodes.includes(
                    language.code,
                  )

                return (
                  <label
                    className={`language-option ${
                      checked ? 'selected' : ''
                    }`}
                    key={language.code}
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      disabled={
                        isSearching ||
                        isBatchAnalyzing
                      }
                      onChange={() =>
                        toggleSearchLanguage(
                          language.code,
                        )
                      }
                    />

                    <span
                      className="language-checkbox"
                      aria-hidden="true"
                    >
                      {checked ? '✓' : ''}
                    </span>

                    <span className="language-labels">
                      <strong>
                        {language.nativeLabel}
                      </strong>

                      {language.label !==
                        language.nativeLabel && (
                        <small>
                          {language.label}
                        </small>
                      )}
                    </span>
                  </label>
                )
              })}
            </div>

            <div className="language-info-note">
              Al pas 12B aquests idiomes controlaran
              les paraules com Careers, Karriere,
              Emploi, Lavora con noi, etc.
            </div>
          </section>

          <div className="custom-job-search">
            <label
              className="field-label"
              htmlFor="custom-job-query"
            >
              Cerca lliure de professió
            </label>

            <input
              id="custom-job-query"
              type="text"
              value={customJobQuery}
              disabled={
                isSearching ||
                isBatchAnalyzing
              }
              onChange={(event) => {
                clearCurrentSearch()
                setCustomJobQuery(
                  event.target.value,
                )
                setNotice(
                  'La cerca lliure ha canviat. Prepara una nova cerca per actualitzar els resultats.',
                )
              }}
              placeholder="Ex.: infermer/a, soldador/a, arquitecte, data analyst..."
            />

            <p className="field-help">
              Pots utilitzar aquesta cerca sola o combinar-la amb els perfils predefinits.
            </p>
          </div>

          <div className="section-title-row">
            <div>
              <p className="field-label">Perfils professionals</p>
              <p className="field-help">
                {selectedProfessionIds.length} seleccionats
              </p>
            </div>

            <div className="small-actions">
              <button
                type="button"
                onClick={selectAllProfessions}
                disabled={isSearching}
              >
                Tots
              </button>

              <button
                type="button"
                onClick={clearProfessions}
                disabled={isSearching}
              >
                Neteja
              </button>
            </div>
          </div>

          <div className="profession-list">
            {PROFESSIONS.map((profession) => {
              const checked = selectedProfessionIds.includes(profession.id)

              return (
                <label
                  className={`profession-option ${checked ? 'selected' : ''}`}
                  key={profession.id}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    disabled={isSearching}
                    onChange={() => toggleProfession(profession.id)}
                  />

                  <span className="custom-checkbox" aria-hidden="true">
                    {checked ? '✓' : ''}
                  </span>

                  <span>
                    <strong>{profession.label}</strong>
                    <small>{profession.description}</small>
                  </span>
                </label>
              )
            })}
          </div>

          <button
            className="primary-button"
            type="button"
            onClick={prepareSearch}
            disabled={
              (
                selectedProfessionIds.length === 0 &&
                customJobQuery.trim().length < 2
              ) ||
              isSearching ||
              isLocating ||
              !resolvedLocation
            }
          >
            {isSearching
              ? 'Cercant organitzacions...'
              : !resolvedLocation
                ? 'Localitza una ubicació'
                : `Preparar cerca a ${resolvedLocation.location_name}`}
          </button>

          <button
            className="secondary-button"
            type="button"
            onClick={expandSearch}
            disabled={!searchPrepared || isSearching}
          >
            Continuar: ampliar fins a {radiusKm + 20} km
          </button>

          <button
            className="text-button"
            type="button"
            onClick={resetSearch}
            disabled={isSearching}
          >
            Reiniciar la cerca
          </button>
        </aside>

        <section className="workspace">
          <div className="welcome-card">
            <div>
              <p className="eyebrow">Àrea de treball</p>
              <h2>Empreses i oportunitats professionals</h2>
              <p>
                Cerca organitzacions oficials i les classifica segons els
                perfils professionals seleccionats.
              </p>
            </div>

            <div className="radius-card">
              <span>Àrea actual</span>
              <strong>{currentArea}</strong>
              <small>
                Increment progressiu de 20 km, sense repetir resultats
              </small>
            </div>
          </div>

          <div className="notice" aria-live="polite">
            <span aria-hidden="true">i</span>
            <p>{notice}</p>
          </div>

          {errorMessage && (
            <div className="notice error-notice" role="alert">
              <span aria-hidden="true">!</span>
              <p>{errorMessage}</p>
            </div>
          )}

          <section className="stats-grid" aria-label="Resum de la cerca">
            <article className="stat-card">
              <span>Resultats rellevants</span>
              <strong>{relevantOrganizations.length}</strong>
              <small>
                {customJobQuery.trim() &&
                selectedProfessionIds.length === 0
                  ? 'Organitzacions potencials per a la cerca lliure'
                  : 'Coincideixen amb els perfils marcats'}
              </small>
            </article>

            <article className="stat-card">
              <span>Organitzacions analitzades</span>
              <strong>{organizations.length}</strong>
              <small>Dades reals obtingudes d’OpenStreetMap</small>
            </article>

            <article className="stat-card">
              <span>Radi actual</span>
              <strong>{radiusKm} km</strong>
              <small>
                {radiusKm === 0
                  ? `Àrea inicial de ${selectedLocationName}`
                  : currentArea}
              </small>
            </article>

            <article className="stat-card">
              <span>Perfils actius</span>
              <strong>
                {selectedProfessions.length +
                  (customJobQuery.trim() ? 1 : 0)}
              </strong>
              <small>
                {customJobQuery.trim()
                  ? `Lliure: ${customJobQuery.trim()}`
                  : selectedProfessions.length > 0
                    ? selectedProfessions
                        .slice(0, 2)
                        .map((profession) => profession.label)
                        .join(' · ')
                    : 'Cap perfil seleccionat'}
              </small>
            </article>
          </section>

          <section className="results-card">
            <div className="results-heading matching-heading">
              <div>
                <p className="eyebrow">Resultats classificats</p>
                <h2>Empreses i centres relacionats</h2>
              </div>

              <div className="results-controls">
                {hiddenLowRelevanceCount > 0 && (
                  <label className="low-relevance-toggle">
                    <input
                      type="checkbox"
                      checked={showLowRelevance}
                      disabled={isBatchAnalyzing}
                      onChange={(event) =>
                        setShowLowRelevance(event.target.checked)
                      }
                    />

                    <span>
                      Mostrar poc relacionats ({hiddenLowRelevanceCount})
                    </span>
                  </label>
                )}

                <div className="batch-controls">
                  {!isBatchAnalyzing ? (
                    <button
                      className="batch-analyze-button"
                      type="button"
                      disabled={
                        unanalyzedVisibleWebsiteCount === 0
                      }
                      onClick={() =>
                        void analyzeVisibleWebsites()
                      }
                    >
                      Analitza webs visibles (
                      {unanalyzedVisibleWebsiteCount})
                    </button>
                  ) : (
                    <>
                      <button
                        className="batch-pause-button"
                        type="button"
                        onClick={toggleBatchPause}
                      >
                        {isBatchPaused ? 'Reprèn' : 'Pausa'}
                      </button>

                      <button
                        className="batch-stop-button"
                        type="button"
                        onClick={stopBatchAnalysis}
                      >
                        Atura
                      </button>
                    </>
                  )}
                </div>

                {isBatchAnalyzing && (
                  <div
                    className="batch-progress-inline"
                    aria-live="polite"
                  >
                    <div className="batch-progress-text">
                      <span>
                        {isBatchPaused ? (
                          <span className="batch-paused-label">
                            En pausa
                          </span>
                        ) : (
                          'Analitzant webs'
                        )}
                      </span>

                      <strong>
                        {batchProgress.completed}/
                        {batchProgress.total}
                      </strong>
                    </div>

                    <progress
                      max={Math.max(batchProgress.total, 1)}
                      value={batchProgress.completed}
                    />
                  </div>
                )}

                <button type="button" disabled>
                  Exporta CSV
                </button>
              </div>
            </div>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Empresa o centre</th>
                    <th>Municipi</th>
                    <th>Distància</th>
                    <th>Perfils coincidents</th>
                    <th>Puntuació</th>
                    <th>Estat</th>
                    <th>Accions</th>
                  </tr>
                </thead>

                <tbody>
                  {isSearching && organizations.length === 0 ? (
                    <tr>
                      <td colSpan={7}>
                        <div className="empty-state">
                          <div
                            className="empty-icon loading-icon"
                            aria-hidden="true"
                          >
                            ◌
                          </div>

                          <h3>Cercant i classificant organitzacions</h3>

                          <p>
                            La consulta d’OpenStreetMap pot trigar uns segons.
                          </p>
                        </div>
                      </td>
                    </tr>
                  ) : visibleOrganizations.length === 0 ? (
                    <tr>
                      <td colSpan={7}>
                        <div className="empty-state">
                          <div className="empty-icon" aria-hidden="true">
                            ◎
                          </div>

                          <h3>
                            {organizations.length === 0
                              ? 'Encara no hi ha resultats'
                              : 'No hi ha coincidències rellevants'}
                          </h3>

                          <p>
                            {organizations.length === 0
                              ? "Selecciona una ubicació i els perfils professionals abans d'iniciar la cerca."
                              : 'Activa «Mostrar poc relacionats» o selecciona més perfils professionals.'}
                          </p>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    visibleOrganizations.map(
                      ({ organization, evaluation }) => (
                        <tr
                          key={organization.id}
                          className={
                            evaluation.isRelevant
                              ? ''
                              : 'low-relevance-row'
                          }
                        >
                          <td>
                            <div className="result-name">
                              <strong>{organization.name}</strong>

                              <small>{organization.category}</small>
                            </div>
                          </td>

                          <td>
                            {organization.municipality ||
                              selectedLocationName}
                          </td>

                          <td>
                            {organization.distanceKm === null
                              ? '—'
                              : `${organization.distanceKm.toFixed(1)} km`}
                          </td>

                          <td>
                            <div
                              className="profile-matches"
                              title={evaluation.reasons.join(' · ')}
                            >
                              {evaluation.matchedProfileLabels.length > 0 ? (
                                <>
                                  {evaluation.matchedProfileLabels
                                    .slice(0, 2)
                                    .map((profileLabel) => (
                                      <span key={profileLabel}>
                                        {profileLabel}
                                      </span>
                                    ))}

                                  {evaluation.matchedProfileLabels.length >
                                    2 && (
                                    <small>
                                      +
                                      {evaluation.matchedProfileLabels.length -
                                        2}{' '}
                                      més
                                    </small>
                                  )}
                                </>
                              ) : (
                                <span className="no-match">
                                  Cap coincidència clara
                                </span>
                              )}

                              {evaluation.reasons.length > 0 && (
                                <small className="match-reason">
                                  {evaluation.reasons[0]}
                                </small>
                              )}
                            </div>
                          </td>

                          <td>
                            <span
                              className={`score-badge score-${evaluation.level}`}
                              title={evaluation.reasons.join(' · ')}
                            >
                              {evaluation.score}/100
                            </span>
                          </td>

                          <td>
                            <span
                              className={`relevance-pill relevance-${evaluation.level}`}
                            >
                              {getRelevanceLabel(evaluation)}
                            </span>
                          </td>

                          <td>
                            {organization.website ? (
                              <div className="row-actions">
                                <div className="row-action-buttons">
                                  <a
                                    className="website-link"
                                    href={organization.website}
                                    target="_blank"
                                    rel="noreferrer"
                                  >
                                    Obre la web
                                  </a>

                                  <button
                                    className="analyze-button"
                                    type="button"
                                    disabled={
                                      isBatchAnalyzing ||
                                      analyzingOrganizationId ===
                                        organization.id
                                    }
                                    onClick={() =>
                                      void analyzeOrganizationWebsite(
                                        organization,
                                      )
                                    }
                                  >
                                    {analyzingOrganizationId ===
                                    organization.id
                                      ? 'Analitzant...'
                                      : isBatchAnalyzing &&
                                          batchQueuedOrganizationIds.includes(
                                            organization.id,
                                          )
                                        ? 'En cua'
                                        : siteAnalyses[organization.id]
                                          ? 'Torna a analitzar'
                                          : 'Analitza la web'}
                                  </button>
                                </div>

                                {siteAnalyses[organization.id] && (
                                  <SiteOpportunityCard
                                    analysis={
                                      siteAnalyses[organization.id]
                                    }
                                  />
                                )}

                                {siteAnalysisErrors[organization.id] && (
                                  <small className="analysis-error">
                                    {
                                      siteAnalysisErrors[
                                        organization.id
                                      ]
                                    }
                                  </small>
                                )}
                              </div>
                            ) : (
                              <span className="no-link">
                                Web no indicada
                              </span>
                            )}
                          </td>
                        </tr>
                      ),
                    )
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </section>
      </main>

      <footer>
        CityJobMap · Projecte local i open source · Sense telemetria
      </footer>
    </div>
  )
}

export default App