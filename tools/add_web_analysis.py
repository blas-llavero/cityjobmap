from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]

APP_PATH = ROOT / "apps" / "dashboard" / "src" / "App.tsx"
CSS_PATH = ROOT / "apps" / "dashboard" / "src" / "App.css"
SERVICE_PATH = (
    ROOT
    / "apps"
    / "dashboard"
    / "src"
    / "services"
    / "siteAnalysisApi.ts"
)


def replace_once(
    text: str,
    old: str,
    new: str,
    description: str,
) -> str:
    occurrences = text.count(old)

    if occurrences != 1:
        raise RuntimeError(
            f"No s'ha pogut aplicar «{description}». "
            f"S'esperava 1 coincidència i se n'han trobat {occurrences}."
        )

    return text.replace(old, new, 1)


SERVICE_CONTENT = r"""export type SiteAnalysisStatus =
  | 'possible_active_offer'
  | 'careers_page'
  | 'contact_page'
  | 'website_only'
  | 'robots_blocked'

export type SiteEvidence = {
  kind: 'offer' | 'careers' | 'contact'
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
  pages_checked: string[]
  evidence: SiteEvidence[]
  blocked_urls: string[]
}

type ApiErrorResponse = {
  detail?: string
}

const API_BASE_URL = 'http://127.0.0.1:8000'

export async function analyzeWebsite(
  website: string,
  signal?: AbortSignal,
): Promise<SiteAnalysis> {
  const response = await fetch(`${API_BASE_URL}/analyze-site`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      website,
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
"""


CSS_CONTENT = r"""

/* Anàlisi de les webs oficials */

.row-actions {
  min-width: 230px;
  display: grid;
  gap: 8px;
}

.row-action-buttons {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 7px;
}

.analyze-button {
  padding: 7px 10px;
  border: 1px solid #99b2ed;
  border-radius: 9px;
  color: #ffffff;
  background: #3568dc;
  font-size: 12px;
  font-weight: 750;
}

.analyze-button:hover:not(:disabled) {
  background: #2857c2;
}

.site-analysis {
  padding: 9px 10px;
  border: 1px solid #dce3ed;
  border-radius: 10px;
  background: #f7f9fc;
}

.site-analysis strong {
  display: block;
  color: #37445a;
  font-size: 11px;
  line-height: 1.4;
}

.site-analysis small {
  display: block;
  margin-top: 6px;
  color: #7b8798;
  font-size: 10px;
  line-height: 1.4;
}

.site-analysis-possible_active_offer {
  border-color: #9edfc9;
  background: #eaf9f3;
}

.site-analysis-careers_page {
  border-color: #b8cbf6;
  background: #eff4ff;
}

.site-analysis-contact_page {
  border-color: #f1d49a;
  background: #fff8e8;
}

.site-analysis-robots_blocked {
  border-color: #e0c7c7;
  background: #faf1f1;
}

.site-analysis-links {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 7px;
}

.site-analysis-links a {
  color: #285bc4;
  font-size: 10px;
  font-weight: 750;
  text-decoration: none;
}

.site-analysis-links a:hover {
  text-decoration: underline;
}

.analysis-error {
  display: block;
  color: #b23434;
  font-size: 10px;
  line-height: 1.4;
}
"""


def main() -> None:
    if not APP_PATH.exists():
        raise RuntimeError(f"No existeix el fitxer {APP_PATH}")

    SERVICE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SERVICE_PATH.write_text(SERVICE_CONTENT, encoding="utf-8")

    backup_path = APP_PATH.with_name(
        "App.tsx.bak-before-site-analysis"
    )

    if not backup_path.exists():
        shutil.copy2(APP_PATH, backup_path)

    app_text = APP_PATH.read_text(encoding="utf-8")

    if (
        "analyzeOrganizationWebsite" in app_text
        and "siteAnalyses" in app_text
    ):
        print("App.tsx ja contenia la integració amb l'API.")
    else:
        app_text = replace_once(
            app_text,
            """import './App.css'
import { evaluateOrganization } from './services/matching'
""",
            """import './App.css'
import { analyzeWebsite } from './services/siteAnalysisApi'
import type { SiteAnalysis } from './services/siteAnalysisApi'
import { evaluateOrganization } from './services/matching'
""",
            "importació del servei d’anàlisi",
        )

        app_text = replace_once(
            app_text,
            """  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const [notice, setNotice] = useState(
""",
            """  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [siteAnalyses, setSiteAnalyses] = useState<
    Record<string, SiteAnalysis>
  >({})
  const [siteAnalysisErrors, setSiteAnalysisErrors] = useState<
    Record<string, string>
  >({})
  const [analyzingOrganizationId, setAnalyzingOrganizationId] = useState<
    string | null
  >(null)

  const [notice, setNotice] = useState(
""",
            "estats de l’anàlisi web",
        )

        app_text = replace_once(
            app_text,
            """    setShowLowRelevance(false)
    setErrorMessage(null)
  }
""",
            """    setShowLowRelevance(false)
    setErrorMessage(null)
    setSiteAnalyses({})
    setSiteAnalysisErrors({})
    setAnalyzingOrganizationId(null)
  }
""",
            "reinici de les anàlisis web",
        )

        app_text = replace_once(
            app_text,
            """  const currentArea =
""",
            """  const analyzeOrganizationWebsite = async (
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
""",
            "funció d’anàlisi d’una empresa",
        )

        app_text = replace_once(
            app_text,
            """                          <td>
                            {organization.website ? (
                              <a
                                className="website-link"
                                href={organization.website}
                                target="_blank"
                                rel="noreferrer"
                              >
                                Obre la web
                              </a>
                            ) : (
                              <span className="no-link">
                                Web no indicada
                              </span>
                            )}
                          </td>
""",
            """                          <td>
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
                                      : siteAnalyses[organization.id]
                                        ? 'Torna a analitzar'
                                        : 'Analitza la web'}
                                  </button>
                                </div>

                                {siteAnalyses[organization.id] && (
                                  <div
                                    className={`site-analysis site-analysis-${
                                      siteAnalyses[organization.id].status
                                    }`}
                                  >
                                    <strong>
                                      {
                                        siteAnalyses[organization.id]
                                          .status_label
                                      }
                                    </strong>

                                    <div className="site-analysis-links">
                                      {siteAnalyses[organization.id]
                                        .career_url && (
                                        <a
                                          href={
                                            siteAnalyses[organization.id]
                                              .career_url ?? undefined
                                          }
                                          target="_blank"
                                          rel="noreferrer"
                                        >
                                          Obre la pàgina de feina
                                        </a>
                                      )}

                                      {siteAnalyses[organization.id]
                                        .contact_url && (
                                        <a
                                          href={
                                            siteAnalyses[organization.id]
                                              .contact_url ?? undefined
                                          }
                                          target="_blank"
                                          rel="noreferrer"
                                        >
                                          Obre el contacte
                                        </a>
                                      )}
                                    </div>

                                    {siteAnalyses[organization.id].evidence
                                      .length > 0 && (
                                      <small>
                                        {
                                          siteAnalyses[organization.id]
                                            .evidence[0].label
                                        }
                                      </small>
                                    )}
                                  </div>
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
""",
            "botons i resultat de l’anàlisi",
        )

        APP_PATH.write_text(app_text, encoding="utf-8")
        print("App.tsx actualitzat correctament.")

    css_text = CSS_PATH.read_text(encoding="utf-8")

    if "/* Anàlisi de les webs oficials */" not in css_text:
        CSS_PATH.write_text(
            css_text + CSS_CONTENT,
            encoding="utf-8",
        )
        print("Estils de l’anàlisi web afegits.")
    else:
        print("Els estils de l’anàlisi web ja existien.")

    print("Servei siteAnalysisApi.ts creat correctament.")
    print("Integració finalitzada.")


if __name__ == "__main__":
    main()