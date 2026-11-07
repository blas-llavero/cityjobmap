from pathlib import Path
import shutil

root = Path.cwd()

app_path = root / "apps" / "dashboard" / "src" / "App.tsx"
css_path = root / "apps" / "dashboard" / "src" / "components" / "LocationMap.css"

backup_path = app_path.with_name(
    "App.tsx.bak-before-map-connect"
)

if not backup_path.exists():
    shutil.copy2(app_path, backup_path)

app = app_path.read_text(encoding="utf-8")


def replace_once(text, old, new, description):
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"{description}: esperava 1 coincidència "
            f"i n'he trobat {count}."
        )

    return text.replace(old, new, 1)


# --------------------------------------------------
# 1. Importar el component del mapa
# --------------------------------------------------

app = replace_once(
    app,
    "import type { OrganizationResult } from './services/overpass'\n",
    (
        "import type { OrganizationResult } from './services/overpass'\n"
        "import { LocationMap } from './components/LocationMap'\n"
    ),
    "Import de LocationMap",
)


# --------------------------------------------------
# 2. Crear la funció que rep el clic del mapa
# --------------------------------------------------

anchor = """  const toggleSearchLanguage = (
"""

map_handler = """  const selectLocationFromMap = (
    latitude: number,
    longitude: number,
  ) => {
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
      `Punt seleccionat al mapa: ${coordinateLabel}. ` +
      'Ja pots iniciar la cerca.',
    )
  }

"""

app = replace_once(
    app,
    anchor,
    map_handler + anchor,
    "Funció selectLocationFromMap",
)


# --------------------------------------------------
# 3. Inserir el mapa sota la cerca escrita
# --------------------------------------------------

location_anchor = """          </div>

          {resolvedLocation && (
"""

map_ui = """          </div>

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
"""

app = replace_once(
    app,
    location_anchor,
    map_ui,
    "Inserció visual del mapa",
)


# --------------------------------------------------
# 4. Evitar mostrar un país buit per a punts del mapa
# --------------------------------------------------

country_old = """                  {resolvedLocation.location_name}
                  {' · '}
                  {resolvedLocation.country_code.toUpperCase()}
"""

country_new = """                  {resolvedLocation.location_name}
                  {resolvedLocation.country_code && (
                    <>
                      {' · '}
                      {resolvedLocation.country_code.toUpperCase()}
                    </>
                  )}
"""

app = replace_once(
    app,
    country_old,
    country_new,
    "País opcional",
)


# --------------------------------------------------
# Guardar App.tsx
# --------------------------------------------------

app_path.write_text(
    app,
    encoding="utf-8",
)


# --------------------------------------------------
# 5. Estil del separador
# --------------------------------------------------

css = css_path.read_text(encoding="utf-8")

separator_css = """

.location-map-separator {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 18px 0 12px;
  color: #667389;
  font-size: 12px;
  font-weight: 700;
}

.location-map-separator::before,
.location-map-separator::after {
  content: "";
  flex: 1;
  height: 1px;
  background: #d6dfed;
}

.location-map-separator span {
  flex: 0 0 auto;
}
"""

if ".location-map-separator {" not in css:
    css += separator_css

css_path.write_text(
    css,
    encoding="utf-8",
)

print()
print("Mapa connectat correctament a CityJobMap.")
print()
print("Còpia de seguretat:")
print(backup_path)
print()