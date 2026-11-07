from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]

APP_PATH = ROOT / "apps" / "dashboard" / "src" / "App.tsx"
CSS_PATH = ROOT / "apps" / "dashboard" / "src" / "App.css"


COMPONENT_CODE = r"""
type OpportunityTone =
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
"""


OLD_ANALYSIS_BLOCK = r"""                                {siteAnalyses[organization.id] && (
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
"""


NEW_ANALYSIS_BLOCK = r"""                                {siteAnalyses[organization.id] && (
                                  <SiteOpportunityCard
                                    analysis={
                                      siteAnalyses[organization.id]
                                    }
                                  />
                                )}
"""


CSS_CONTENT = r"""

/* Presentació clara de les oportunitats laborals */

.opportunity-card {
  padding: 11px;
  border: 1px solid #dbe2ec;
  border-radius: 11px;
  background: #f7f9fc;
}

.opportunity-heading {
  display: flex;
  align-items: flex-start;
  gap: 7px;
}

.opportunity-heading strong {
  color: #344158;
  font-size: 11px;
  line-height: 1.4;
}

.opportunity-indicator {
  width: 9px;
  height: 9px;
  flex: 0 0 auto;
  margin-top: 3px;
  border-radius: 50%;
  background: #8793a4;
}

.opportunity-card p {
  margin: 7px 0 0;
  color: #6e7a8d;
  font-size: 10px;
  line-height: 1.45;
}

.opportunity-offer {
  border-color: #8fd6be;
  background: #e8f8f1;
}

.opportunity-offer .opportunity-indicator {
  background: #12a576;
  box-shadow: 0 0 0 4px rgba(18, 165, 118, 0.12);
}

.opportunity-careers {
  border-color: #a9c0f5;
  background: #eef3ff;
}

.opportunity-careers .opportunity-indicator {
  background: #3970ff;
  box-shadow: 0 0 0 4px rgba(57, 112, 255, 0.12);
}

.opportunity-contact {
  border-color: #edcc8b;
  background: #fff7e7;
}

.opportunity-contact .opportunity-indicator {
  background: #d49315;
  box-shadow: 0 0 0 4px rgba(212, 147, 21, 0.12);
}

.opportunity-none {
  border-color: #d9dfe8;
  background: #f5f7fa;
}

.opportunity-blocked {
  border-color: #e2baba;
  background: #fff1f1;
}

.opportunity-blocked .opportunity-indicator {
  background: #cf4747;
  box-shadow: 0 0 0 4px rgba(207, 71, 71, 0.12);
}

.opportunity-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 9px;
}

.opportunity-primary-link,
.opportunity-secondary-link {
  display: inline-block;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 800;
  text-decoration: none;
}

.opportunity-primary-link {
  padding: 7px 9px;
  color: #ffffff;
  background: #315fca;
}

.opportunity-primary-link:hover {
  background: #244da9;
}

.opportunity-secondary-link {
  padding: 6px 3px;
  color: #315fca;
}

.opportunity-secondary-link:hover {
  text-decoration: underline;
}

.opportunity-evidence {
  display: block;
  margin-top: 9px;
  padding-top: 8px;
  border-top: 1px solid rgba(90, 107, 134, 0.15);
  color: #687588;
  font-size: 9px;
  line-height: 1.45;
}

.pages-checked {
  display: block;
  margin-top: 7px;
  color: #929cab;
  font-size: 9px;
}
"""


def main() -> None:
    if not APP_PATH.exists():
        raise RuntimeError(
            f"No s'ha trobat el fitxer {APP_PATH}"
        )

    backup_path = APP_PATH.with_name(
        "App.tsx.bak-before-opportunity-status"
    )

    if not backup_path.exists():
        shutil.copy2(APP_PATH, backup_path)

    app_text = APP_PATH.read_text(encoding="utf-8")

    if "function SiteOpportunityCard" not in app_text:
        marker = "function App() {"

        if marker not in app_text:
            raise RuntimeError(
                "No s'ha trobat el punt on inserir el component."
            )

        app_text = app_text.replace(
            marker,
            COMPONENT_CODE + "\n\n" + marker,
            1,
        )

        print("Component d'estat laboral afegit.")
    else:
        print("El component d'estat laboral ja existia.")

    if OLD_ANALYSIS_BLOCK in app_text:
        app_text = app_text.replace(
            OLD_ANALYSIS_BLOCK,
            NEW_ANALYSIS_BLOCK,
            1,
        )

        print("Presentació antiga substituïda.")
    elif NEW_ANALYSIS_BLOCK in app_text:
        print("La presentació nova ja estava aplicada.")
    else:
        raise RuntimeError(
            "No s'ha pogut localitzar el bloc de resultats "
            "de l'anàlisi web."
        )

    APP_PATH.write_text(
        app_text,
        encoding="utf-8",
    )

    css_text = CSS_PATH.read_text(encoding="utf-8")

    if (
        "/* Presentació clara de les oportunitats laborals */"
        not in css_text
    ):
        CSS_PATH.write_text(
            css_text + CSS_CONTENT,
            encoding="utf-8",
        )

        print("Estils nous afegits.")
    else:
        print("Els estils nous ja existien.")

    print("Millora completada correctament.")


if __name__ == "__main__":
    main()