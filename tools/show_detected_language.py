from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

APP_PATH = (
    ROOT
    / "apps"
    / "dashboard"
    / "src"
    / "App.tsx"
)

CSS_PATH = (
    ROOT
    / "apps"
    / "dashboard"
    / "src"
    / "App.css"
)


def main():
    app = APP_PATH.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------
    # Helper per mostrar el nom de l'idioma
    # --------------------------------------------------

    if "function formatAnalysisLanguage(" not in app:
        marker = """function SiteOpportunityCard({
"""

        helper = """function formatAnalysisLanguage(
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

"""

        if marker not in app:
            raise RuntimeError(
                "No s'ha trobat SiteOpportunityCard."
            )

        app = app.replace(
            marker,
            helper + marker,
            1,
        )

    # --------------------------------------------------
    # Informació dins la targeta
    # --------------------------------------------------

    old = """      <p>{view.description}</p>

      <div className="opportunity-actions">
"""

    new = """      <p>{view.description}</p>

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
"""

    if old in app:
        app = app.replace(
            old,
            new,
            1,
        )
    elif "detected-language-panel" not in app:
        raise RuntimeError(
            "No s'ha trobat el punt "
            "on mostrar l'idioma."
        )

    APP_PATH.write_text(
        app,
        encoding="utf-8",
    )

    # --------------------------------------------------
    # CSS
    # --------------------------------------------------

    css = CSS_PATH.read_text(
        encoding="utf-8"
    )

    marker = (
        "/* Detecció automàtica de l'idioma web */"
    )

    if marker not in css:
        css += r"""

/* Detecció automàtica de l'idioma web */

.detected-language-panel {
  margin-top: 8px;
  padding: 7px 8px;
  border: 1px solid rgba(70, 95, 135, 0.14);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.58);
}

.detected-language-panel span,
.detected-language-panel small {
  display: block;
  line-height: 1.4;
}

.detected-language-panel span {
  color: #526177;
  font-size: 9.5px;
}

.detected-language-panel strong {
  color: #294e9f;
}

.detected-language-panel small {
  margin-top: 3px;
  color: #8390a2;
  font-size: 8.5px;
}
"""

        CSS_PATH.write_text(
            css,
            encoding="utf-8",
        )

    print(
        "Idioma detectat afegit al dashboard."
    )


if __name__ == "__main__":
    main()