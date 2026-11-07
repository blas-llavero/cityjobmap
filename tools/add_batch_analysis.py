from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]

APP_PATH = ROOT / "apps" / "dashboard" / "src" / "App.tsx"
CSS_PATH = ROOT / "apps" / "dashboard" / "src" / "App.css"


HELPERS_CODE = r"""
const BATCH_DELAY_MS = 1500

const SITE_ANALYSIS_PRIORITY: Record<
  SiteAnalysis['status'],
  number
> = {
  possible_active_offer: 0,
  careers_page: 1,
  contact_page: 2,
  website_only: 3,
  robots_blocked: 4,
}

function waitForMilliseconds(
  milliseconds: number,
  signal: AbortSignal,
): Promise<void> {
  return new Promise((resolve, reject) => {
    let timerId: number | undefined

    const handleAbort = () => {
      if (timerId !== undefined) {
        window.clearTimeout(timerId)
      }

      reject(
        new DOMException(
          'Operació cancel·lada',
          'AbortError',
        ),
      )
    }

    if (signal.aborted) {
      handleAbort()
      return
    }

    timerId = window.setTimeout(() => {
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
"""


CSS_CONTENT = r"""

/* Anàlisi automàtica per lots */

.batch-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 7px;
}

.batch-analyze-button,
.batch-pause-button,
.batch-stop-button {
  padding: 8px 11px;
  border-radius: 9px;
  font-size: 11px;
  font-weight: 800;
}

.batch-analyze-button {
  border: 1px solid #315fca;
  color: #ffffff;
  background: #315fca;
}

.batch-analyze-button:hover:not(:disabled) {
  background: #244fae;
}

.batch-pause-button {
  border: 1px solid #d6a444;
  color: #79540b;
  background: #fff5dc;
}

.batch-stop-button {
  border: 1px solid #e1a6a6;
  color: #9a3030;
  background: #fff0f0;
}

.batch-progress-inline {
  min-width: 190px;
  display: grid;
  gap: 5px;
}

.batch-progress-text {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  color: #56647a;
  font-size: 10px;
  font-weight: 700;
}

.batch-progress-inline progress {
  width: 100%;
  height: 8px;
  overflow: hidden;
  border: 0;
  border-radius: 999px;
  accent-color: #3970ff;
}

.batch-progress-inline progress::-webkit-progress-bar {
  border-radius: 999px;
  background: #e5eaf2;
}

.batch-progress-inline progress::-webkit-progress-value {
  border-radius: 999px;
  background: #3970ff;
}

.batch-paused-label {
  color: #956500;
  font-weight: 800;
}

@media (max-width: 900px) {
  .results-controls {
    justify-content: flex-start;
  }

  .batch-progress-inline {
    width: 100%;
  }
}
"""


def replace_once(
    text: str,
    old: str,
    new: str,
    description: str,
) -> str:
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"No s'ha pogut aplicar «{description}». "
            f"S'esperava 1 coincidència i se n'han trobat {count}."
        )

    return text.replace(old, new, 1)


def main() -> None:
    if not APP_PATH.exists():
        raise RuntimeError(
            f"No s'ha trobat el fitxer {APP_PATH}"
        )

    backup_path = APP_PATH.with_name(
        "App.tsx.bak-before-batch-analysis"
    )

    if not backup_path.exists():
        shutil.copy2(APP_PATH, backup_path)

    app_text = APP_PATH.read_text(encoding="utf-8")

    if "const BATCH_DELAY_MS" not in app_text:
        marker = "function App() {"

        if marker not in app_text:
            raise RuntimeError(
                "No s'ha trobat el punt on inserir "
                "les funcions auxiliars."
            )

        app_text = app_text.replace(
            marker,
            HELPERS_CODE + "\n\n" + marker,
            1,
        )

        print("Funcions auxiliars afegides.")
    else:
        print("Les funcions auxiliars ja existien.")

    old_states = """  const [analyzingOrganizationId, setAnalyzingOrganizationId] = useState<
    string | null
  >(null)

  const [notice, setNotice] = useState(
"""

    new_states = """  const [analyzingOrganizationId, setAnalyzingOrganizationId] = useState<
    string | null
  >(null)
  const [isBatchAnalyzing, setIsBatchAnalyzing] = useState(false)
  const [isBatchPaused, setIsBatchPaused] = useState(false)
  const [batchProgress, setBatchProgress] = useState({
    completed: 0,
    total: 0,
  })

  const [notice, setNotice] = useState(
"""

    if "const [isBatchAnalyzing" not in app_text:
        app_text = replace_once(
            app_text,
            old_states,
            new_states,
            "els estats de l'anàlisi per lots",
        )

        print("Estats de l'anàlisi per lots afegits.")
    else:
        print("Els estats de l'anàlisi per lots ja existien.")

    old_refs = """  const searchControllerRef = useRef<AbortController | null>(null)

  const selectedProfessions = useMemo(
"""

    new_refs = """  const searchControllerRef = useRef<AbortController | null>(null)
  const batchControllerRef = useRef<AbortController | null>(null)
  const batchPausedRef = useRef(false)

  const selectedProfessions = useMemo(
"""

    if "const batchControllerRef" not in app_text:
        app_text = replace_once(
            app_text,
            old_refs,
            new_refs,
            "les referències de control del lot",
        )

        print("Controls interns del lot afegits.")
    else:
        print("Els controls interns del lot ja existien.")

    old_visible = """  const visibleOrganizations = showLowRelevance
    ? evaluatedOrganizations
    : relevantOrganizations

  const hiddenLowRelevanceCount =
    evaluatedOrganizations.length - relevantOrganizations.length
"""

    new_visible = """  const visibleOrganizations = useMemo(() => {
    const baseOrganizations = showLowRelevance
      ? evaluatedOrganizations
      : relevantOrganizations

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
"""

    if "unanalyzedVisibleWebsiteCount" not in app_text:
        app_text = replace_once(
            app_text,
            old_visible,
            new_visible,
            "l'ordenació dels resultats",
        )

        print("Ordenació per oportunitat afegida.")
    else:
        print("L'ordenació per oportunitat ja existia.")

    old_clear = """    setSiteAnalyses({})
    setSiteAnalysisErrors({})
    setAnalyzingOrganizationId(null)
  }
"""

    new_clear = """    batchControllerRef.current?.abort()
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
  }
"""

    if "batchControllerRef.current?.abort()" not in app_text:
        app_text = replace_once(
            app_text,
            old_clear,
            new_clear,
            "el reinici de l'anàlisi per lots",
        )

        print("Reinici del lot afegit.")
    else:
        print("El reinici del lot ja existia.")

    old_analysis_function = """  const analyzeOrganizationWebsite = async (
    organization: OrganizationResult,
  ) => {
    if (!organization.website) {
      return
    }

    setAnalyzingOrganizationId(organization.id)

    setSiteAnalysisErrors((currentErrors) => {
      const nextErrors = { ...currentErrors }
      delete nextErrors[organization.id]
      return nextErrors
    })

    try {
      const analysis = await analyzeWebsite(organization.website)

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

  const currentArea =
"""

    new_analysis_function = """  const analyzeOrganizationWebsite = async (
    organization: OrganizationResult,
  ) => {
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
      const analysis = await analyzeWebsite(organization.website)

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

  const currentArea =
"""

    if "const analyzeVisibleWebsites" not in app_text:
        app_text = replace_once(
            app_text,
            old_analysis_function,
            new_analysis_function,
            "les funcions d'anàlisi automàtica",
        )

        print("Anàlisi automàtica afegida.")
    else:
        print("L'anàlisi automàtica ja existia.")

    old_controls = """              <div className="results-controls">
                {hiddenLowRelevanceCount > 0 && (
                  <label className="low-relevance-toggle">
                    <input
                      type="checkbox"
                      checked={showLowRelevance}
                      onChange={(event) =>
                        setShowLowRelevance(event.target.checked)
                      }
                    />

                    <span>
                      Mostrar poc relacionats ({hiddenLowRelevanceCount})
                    </span>
                  </label>
                )}

                <button type="button" disabled>
                  Exporta CSV
                </button>
              </div>
"""

    new_controls = """              <div className="results-controls">
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
"""

    if "Analitza webs visibles" not in app_text:
        app_text = replace_once(
            app_text,
            old_controls,
            new_controls,
            "els controls de l'anàlisi per lots",
        )

        print("Botons de l'anàlisi per lots afegits.")
    else:
        print("Els botons del lot ja existien.")

    old_disabled = """                                    disabled={
                                      analyzingOrganizationId ===
                                      organization.id
                                    }
"""

    new_disabled = """                                    disabled={
                                      isBatchAnalyzing ||
                                      analyzingOrganizationId ===
                                        organization.id
                                    }
"""

    if "isBatchAnalyzing ||" not in app_text:
        app_text = replace_once(
            app_text,
            old_disabled,
            new_disabled,
            "el bloqueig dels botons individuals",
        )

        print("Botons individuals coordinats amb el lot.")
    else:
        print("Els botons individuals ja estaven coordinats.")

    APP_PATH.write_text(
        app_text,
        encoding="utf-8",
    )

    css_text = CSS_PATH.read_text(encoding="utf-8")

    if "/* Anàlisi automàtica per lots */" not in css_text:
        CSS_PATH.write_text(
            css_text + CSS_CONTENT,
            encoding="utf-8",
        )

        print("Estils de l'anàlisi per lots afegits.")
    else:
        print("Els estils de l'anàlisi per lots ja existien.")

    print("Anàlisi automàtica instal·lada correctament.")


if __name__ == "__main__":
    main()