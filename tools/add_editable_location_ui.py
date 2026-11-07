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


def replace_once(text, old, new, description):
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"No s'ha pogut aplicar «{description}». "
            f"Coincidències trobades: {count}"
        )

    return text.replace(old, new, 1)


def main():
    app = APP_PATH.read_text(encoding="utf-8")

    # --------------------------------------------------
    # Imports
    # --------------------------------------------------

    if "./services/locationApi" not in app:
        app = replace_once(
            app,
            """import { evaluateOrganization } from './services/matching'
""",
            """import { geocodeLocation } from './services/locationApi'
import type { GeocodedLocation } from './services/locationApi'
import { evaluateOrganization } from './services/matching'
""",
            "importació del servei de localització",
        )

    # --------------------------------------------------
    # Estats
    # --------------------------------------------------

    if "const [locationQuery" not in app:
        marker = """  const [radiusKm, setRadiusKm] = useState(0)
"""

        states = """  const [locationQuery, setLocationQuery] =
    useState('Reus, Spain')

  const [resolvedLocation, setResolvedLocation] =
    useState<GeocodedLocation | null>({
      query: 'Reus, Spain',
      display_name:
        'Reus, Baix Camp, Tarragona, Catalonia, Spain',
      latitude: 41.1555564,
      longitude: 1.1076133,
      country_code: 'es',
      location_name: 'Reus',
    })

  const [isLocating, setIsLocating] = useState(false)
  const [locationError, setLocationError] =
    useState<string | null>(null)

"""

        app = replace_once(
            app,
            marker,
            states + marker,
            "estats de la ubicació",
        )

    # --------------------------------------------------
    # Funcions del localitzador
    # --------------------------------------------------

    if "const locateSearchLocation" not in app:
        marker = """  const toggleProfession = (professionId: string) => {
"""

        functions = """  const handleLocationQueryChange = (
    value: string,
  ) => {
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

"""

        app = replace_once(
            app,
            marker,
            functions + marker,
            "funcions del localitzador",
        )

    # --------------------------------------------------
    # Protecció temporal del Pas 11B
    # --------------------------------------------------

    if "Encara no hem connectat aquesta ubicació a Overpass" not in app:
        marker = """  const prepareSearch = async () => {
    if (selectedProfessionIds.length === 0) {
"""

        replacement = """  const prepareSearch = async () => {
    if (!resolvedLocation) {
      setNotice(
        'Primer has de localitzar una ubicació vàlida.',
      )
      return
    }

    if (
      resolvedLocation.location_name
        .toLocaleLowerCase('ca') !== 'reus'
    ) {
      setNotice(
        'Ubicació validada correctament. Encara no hem connectat aquesta ubicació a Overpass; ho farem al pas 11C.',
      )
      return
    }

    if (selectedProfessionIds.length === 0) {
"""

        app = replace_once(
            app,
            marker,
            replacement,
            "protecció temporal de la cerca",
        )

    # --------------------------------------------------
    # Àrea actual dinàmica
    # --------------------------------------------------

    old_area = """  const currentArea =
    radiusKm === 0 ? 'Municipi de Reus' : `Fins a ${radiusKm} km de Reus`
"""

    new_area = """  const selectedLocationName =
    resolvedLocation?.location_name ?? 'Ubicació pendent'

  const locationReadyForCurrentSearch =
    resolvedLocation?.location_name
      .toLocaleLowerCase('ca') === 'reus'

  const currentArea =
    radiusKm === 0
      ? selectedLocationName
      : `Fins a ${radiusKm} km de ${selectedLocationName}`
"""

    if old_area in app:
        app = app.replace(
            old_area,
            new_area,
            1,
        )

    # --------------------------------------------------
    # Camp d'ubicació
    # --------------------------------------------------

    old_location = """          <label className="field-label" htmlFor="base-location">
            Ubicació inicial
          </label>

          <div className="location-field">
            <span aria-hidden="true">⌖</span>
            <input
              id="base-location"
              type="text"
              value="Reus, Catalunya"
              readOnly
            />
          </div>
"""

    new_location = """          <label className="field-label" htmlFor="base-location">
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
                  {' · '}
                  {resolvedLocation.country_code.toUpperCase()}
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

          {resolvedLocation &&
            !locationReadyForCurrentSearch && (
              <div className="location-transition-note">
                Ubicació validada. Al pas 11C la
                connectarem amb la cerca d’empreses.
              </div>
            )}
"""

    if old_location in app:
        app = app.replace(
            old_location,
            new_location,
            1,
        )
    elif "className=\"location-search-row\"" not in app:
        raise RuntimeError(
            "No s'ha pogut localitzar el camp antic d'ubicació."
        )

    # --------------------------------------------------
    # Botó principal
    # --------------------------------------------------

    old_button = """            disabled={selectedProfessionIds.length === 0 || isSearching}
          >
            {isSearching
              ? 'Cercant organitzacions...'
              : 'Preparar cerca inicial a Reus'}
          </button>
"""

    new_button = """            disabled={
              selectedProfessionIds.length === 0 ||
              isSearching ||
              isLocating ||
              !resolvedLocation ||
              !locationReadyForCurrentSearch
            }
          >
            {isSearching
              ? 'Cercant organitzacions...'
              : !resolvedLocation
                ? 'Localitza una ubicació'
                : locationReadyForCurrentSearch
                  ? `Preparar cerca a ${resolvedLocation.location_name}`
                  : 'Ubicació preparada · falta el pas 11C'}
          </button>
"""

    if old_button in app:
        app = app.replace(
            old_button,
            new_button,
            1,
        )
    elif "Ubicació preparada · falta el pas 11C" not in app:
        raise RuntimeError(
            "No s'ha pogut localitzar el botó principal."
        )

    APP_PATH.write_text(
        app,
        encoding="utf-8",
    )

    # --------------------------------------------------
    # CSS
    # --------------------------------------------------

    css = CSS_PATH.read_text(encoding="utf-8")

    css_marker = "/* Ubicació editable internacional */"

    if css_marker not in css:
        css += r"""

/* Ubicació editable internacional */

.location-search-row {
  display: flex;
  align-items: stretch;
  gap: 8px;
  margin-bottom: 10px;
}

.location-search-row .location-field {
  flex: 1;
  min-width: 0;
  margin-bottom: 0;
}

.location-search-row .location-field input {
  min-width: 0;
}

.locate-button {
  flex: 0 0 auto;
  min-width: 88px;
  padding: 0 13px;
  border: 1px solid #9db5ee;
  border-radius: 12px;
  color: #2d5cc3;
  background: #eef3ff;
  font-size: 12px;
  font-weight: 800;
}

.locate-button:hover:not(:disabled) {
  border-color: #6e92e7;
  background: #e3ebff;
}

.resolved-location-card {
  display: grid;
  grid-template-columns: 24px minmax(0, 1fr);
  gap: 9px;
  margin-bottom: 10px;
  padding: 10px 11px;
  border: 1px solid #a8dcc9;
  border-radius: 11px;
  background: #edf9f5;
}

.resolved-location-check {
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  color: #ffffff;
  background: #24a979;
  font-size: 12px;
  font-weight: 900;
}

.resolved-location-card strong,
.resolved-location-card small {
  display: block;
}

.resolved-location-card strong {
  color: #17654d;
  font-size: 12px;
}

.resolved-location-card small {
  margin-top: 3px;
  overflow-wrap: anywhere;
  color: #688175;
  font-size: 9.5px;
  line-height: 1.4;
}

.location-error {
  margin-bottom: 10px;
  padding: 9px 10px;
  border: 1px solid #edb7b7;
  border-radius: 10px;
  color: #a43232;
  background: #fff1f1;
  font-size: 10px;
  line-height: 1.45;
}

.location-transition-note {
  margin-bottom: 20px;
  padding: 9px 10px;
  border: 1px solid #efd29b;
  border-radius: 10px;
  color: #835e16;
  background: #fff8e9;
  font-size: 10px;
  line-height: 1.45;
}

@media (max-width: 480px) {
  .location-search-row {
    flex-direction: column;
  }

  .locate-button {
    min-height: 42px;
  }
}
"""

        CSS_PATH.write_text(
            css,
            encoding="utf-8",
        )

    print(
        "Pas 11B aplicat correctament."
    )


if __name__ == "__main__":
    main()