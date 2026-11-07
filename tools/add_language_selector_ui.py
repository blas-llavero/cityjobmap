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
            f"Coincidències trobades: {count}"
        )

    return text.replace(old, new, 1)


def main() -> None:
    app = APP_PATH.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------
    # 1. Tipus i llista d'idiomes
    # --------------------------------------------------

    if "type SearchLanguageCode" not in app:
        marker = """const PROFESSIONS: Profession[] = [
"""

        language_code = """type SearchLanguageCode =
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

"""

        app = replace_once(
            app,
            marker,
            language_code + marker,
            "la definició dels idiomes",
        )

    # --------------------------------------------------
    # 2. Estat dels idiomes
    # --------------------------------------------------

    if "const [selectedLanguageCodes" not in app:
        marker = """  const [selectedProfessionIds, setSelectedProfessionIds] = useState<string[]>([
"""

        # Busquem el final de l'estat dels perfils de forma segura.
        start = app.find(marker)

        if start < 0:
            raise RuntimeError(
                "No s'ha trobat l'estat selectedProfessionIds."
            )

        search_from = start + len(marker)

        end_marker = """  ])

"""

        end = app.find(
            end_marker,
            search_from,
        )

        if end < 0:
            raise RuntimeError(
                "No s'ha trobat el final de selectedProfessionIds."
            )

        insertion_point = end + len(end_marker)

        language_state = """  const [selectedLanguageCodes, setSelectedLanguageCodes] =
    useState<SearchLanguageCode[]>(['en'])

"""

        app = (
            app[:insertion_point]
            + language_state
            + app[insertion_point:]
        )

    # --------------------------------------------------
    # 3. Funcions del selector
    # --------------------------------------------------

    if "const toggleSearchLanguage" not in app:
        marker = """  const toggleProfession = (professionId: string) => {
"""

        functions = """  const toggleSearchLanguage = (
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

"""

        app = replace_once(
            app,
            marker,
            functions + marker,
            "les funcions del selector d'idiomes",
        )

    # --------------------------------------------------
    # 4. Interfície del selector
    # --------------------------------------------------

    if 'className="language-section"' not in app:
        marker = """          <div className="section-title-row">
            <div>
              <p className="field-label">Perfils professionals</p>
"""

        language_ui = """          <section className="language-section">
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

"""

        app = replace_once(
            app,
            marker,
            language_ui + marker,
            "la interfície dels idiomes",
        )

    APP_PATH.write_text(
        app,
        encoding="utf-8",
    )

    # --------------------------------------------------
    # 5. Estils
    # --------------------------------------------------

    css = CSS_PATH.read_text(
        encoding="utf-8"
    )

    css_marker = (
        "/* Selector internacional d'idiomes */"
    )

    if css_marker not in css:
        css += r"""

/* Selector internacional d'idiomes */

.language-section {
  margin-bottom: 24px;
}

.language-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 7px;
  margin-top: 12px;
}

.language-option {
  position: relative;
  min-width: 0;
  display: grid;
  grid-template-columns: 20px minmax(0, 1fr);
  align-items: center;
  gap: 8px;
  padding: 9px 10px;
  border: 1px solid #e0e6ef;
  border-radius: 11px;
  background: #ffffff;
  cursor: pointer;
  transition:
    border-color 150ms ease,
    background-color 150ms ease,
    transform 150ms ease;
}

.language-option:hover {
  transform: translateY(-1px);
  border-color: #adc2fa;
}

.language-option.selected {
  border-color: #84a4f7;
  background: #f2f6ff;
}

.language-option input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.language-checkbox {
  width: 20px;
  height: 20px;
  display: grid;
  place-items: center;
  border: 1.5px solid #b9c5d8;
  border-radius: 6px;
  color: #ffffff;
  background: #ffffff;
  font-size: 12px;
  font-weight: 900;
}

.language-option.selected
.language-checkbox {
  border-color: #3970ff;
  background: #3970ff;
}

.language-labels {
  min-width: 0;
}

.language-labels strong,
.language-labels small {
  display: block;
}

.language-labels strong {
  overflow: hidden;
  color: #263550;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.language-labels small {
  margin-top: 2px;
  color: #7c8798;
  font-size: 9px;
}

.language-info-note {
  margin-top: 9px;
  padding: 8px 10px;
  border: 1px solid #dbe5fa;
  border-radius: 9px;
  color: #68778f;
  background: #f6f8fd;
  font-size: 9.5px;
  line-height: 1.45;
}

@media (max-width: 480px) {
  .language-grid {
    grid-template-columns: 1fr;
  }
}
"""

        CSS_PATH.write_text(
            css,
            encoding="utf-8",
        )

    print(
        "Pas 12A aplicat correctament."
    )


if __name__ == "__main__":
    main()