from pathlib import Path
import re
import shutil

root = Path.cwd()

app_path = (
    root / "apps" / "dashboard" / "src" / "App.tsx"
)

location_api_path = (
    root
    / "apps"
    / "dashboard"
    / "src"
    / "services"
    / "locationApi.ts"
)

backend_path = (
    root
    / "services"
    / "api"
    / "app"
    / "main.py"
)


def backup(path: Path, suffix: str):
    target = path.with_name(
        path.name + suffix
    )

    if not target.exists():
        shutil.copy2(path, target)

    return target


backup(
    app_path,
    ".bak-before-reverse-geocode",
)

backup(
    location_api_path,
    ".bak-before-reverse-geocode",
)

backup(
    backend_path,
    ".bak-before-reverse-geocode",
)


# ==================================================
# BACKEND
# ==================================================

backend = backend_path.read_text(
    encoding="utf-8",
)

if "NOMINATIM_REVERSE_URL" not in backend:

    pattern = re.compile(
        r'(NOMINATIM_SEARCH_URL\s*=\s*\(\s*'
        r'["\']https://nominatim\.openstreetmap\.org/search["\']'
        r'\s*\)\s*)'
    )

    replacement = (
        r'\1'
        '\nNOMINATIM_REVERSE_URL = (\n'
        '    "https://nominatim.openstreetmap.org/reverse"\n'
        ')\n'
    )

    backend, count = pattern.subn(
        replacement,
        backend,
        count=1,
    )

    if count != 1:
        raise RuntimeError(
            "No s'ha trobat NOMINATIM_SEARCH_URL."
        )


endpoint = r'''

class ReverseGeocodeRequest(BaseModel):
    latitude: float = Field(
        ge=-90.0,
        le=90.0,
    )
    longitude: float = Field(
        ge=-180.0,
        le=180.0,
    )


@app.post("/reverse-geocode-location")
async def reverse_geocode_location(
    payload: ReverseGeocodeRequest,
):
    params = {
        "format": "jsonv2",
        "lat": f"{payload.latitude:.7f}",
        "lon": f"{payload.longitude:.7f}",
        "zoom": "13",
        "addressdetails": "1",
        "layer": "address",
    }

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                NOMINATIM_REVERSE_URL,
                params=params,
                headers=headers,
            )

            response.raise_for_status()

    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail=(
                "No s'ha pogut consultar "
                "el servei de localització."
            ),
        ) from error

    try:
        data = response.json()
    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail=(
                "El servei de localització "
                "ha retornat una resposta no vàlida."
            ),
        ) from error

    if (
        not isinstance(data, dict)
        or data.get("error")
    ):
        raise HTTPException(
            status_code=404,
            detail=(
                "No s'ha pogut identificar "
                "aquest punt del mapa."
            ),
        )

    address = data.get("address")

    if not isinstance(address, dict):
        address = {}

    preferred_fields = (
        "city",
        "town",
        "village",
        "municipality",
        "borough",
        "suburb",
        "county",
        "state",
        "country",
    )

    location_name = None

    for field in preferred_fields:
        value = address.get(field)

        if (
            isinstance(value, str)
            and value.strip()
        ):
            location_name = value.strip()
            break

    if not location_name:
        name = data.get("name")

        if (
            isinstance(name, str)
            and name.strip()
        ):
            location_name = name.strip()

    if not location_name:
        location_name = "Punt del mapa"

    display_name = data.get(
        "display_name",
        location_name,
    )

    if not isinstance(display_name, str):
        display_name = location_name

    country_code = address.get(
        "country_code",
        "",
    )

    if not isinstance(country_code, str):
        country_code = ""

    coordinate_query = (
        f"{payload.latitude:.5f}, "
        f"{payload.longitude:.5f}"
    )

    return {
        "query": coordinate_query,
        "display_name": display_name,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "country_code": (
            country_code
            .strip()
            .lower()
        ),
        "location_name": location_name,
        "bounding_box": None,
    }
'''

if (
    '@app.post("/reverse-geocode-location")'
    not in backend
):
    backend = (
        backend.rstrip()
        + "\n"
        + endpoint
        + "\n"
    )

backend_path.write_text(
    backend,
    encoding="utf-8",
)


# ==================================================
# FRONTEND API
# ==================================================

location_api = location_api_path.read_text(
    encoding="utf-8",
)

reverse_function = r'''

export async function reverseGeocodeLocation(
  latitude: number,
  longitude: number,
  signal?: AbortSignal,
): Promise<GeocodedLocation> {
  const response = await fetch(
    `${API_BASE_URL}/reverse-geocode-location`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        latitude,
        longitude,
      }),
      signal,
    },
  )

  if (!response.ok) {
    let message =
      `La geocodificació inversa ha retornat ` +
      `l’error ${response.status}.`

    try {
      const errorData =
        (await response.json()) as ApiErrorResponse

      if (errorData.detail) {
        message = errorData.detail
      }
    } catch {
      // Conservem el missatge genèric.
    }

    throw new Error(message)
  }

  return (
    await response.json()
  ) as GeocodedLocation
}
'''

if (
    "export async function reverseGeocodeLocation"
    not in location_api
):
    location_api = (
        location_api.rstrip()
        + "\n"
        + reverse_function
        + "\n"
    )

location_api_path.write_text(
    location_api,
    encoding="utf-8",
)


# ==================================================
# APP.TSX
# ==================================================

app = app_path.read_text(
    encoding="utf-8",
)


# Import
old_import = (
    "import { geocodeLocation } "
    "from './services/locationApi'"
)

new_import = (
    "import {\n"
    "  geocodeLocation,\n"
    "  reverseGeocodeLocation,\n"
    "} from './services/locationApi'"
)

if old_import in app:
    app = app.replace(
        old_import,
        new_import,
        1,
    )


# Refs per evitar resultats antics
ref_anchor = (
    "  const searchControllerRef = "
    "useRef<AbortController | null>(null)"
)

ref_code = """  const mapSelectionIdRef = useRef(0)
  const reverseGeocodeTimerRef =
    useRef<number | null>(null)

"""

if "const mapSelectionIdRef" not in app:
    if ref_anchor not in app:
        raise RuntimeError(
            "No s'ha trobat searchControllerRef."
        )

    app = app.replace(
        ref_anchor,
        ref_code + ref_anchor,
        1,
    )


# Quan s'escriu una ciutat, cancel·lar
# una identificació pendent del mapa.
change_anchor = """  ) => {
    setLocationQuery(value)
    setResolvedLocation(null)
"""

change_new = """  ) => {
    mapSelectionIdRef.current += 1

    if (reverseGeocodeTimerRef.current !== null) {
      window.clearTimeout(
        reverseGeocodeTimerRef.current,
      )

      reverseGeocodeTimerRef.current = null
    }

    setLocationQuery(value)
    setResolvedLocation(null)
"""

if (
    change_anchor in app
    and "mapSelectionIdRef.current += 1"
    not in app[
        app.find("const handleLocationQueryChange"):
        app.find("const locateSearchLocation")
    ]
):
    app = app.replace(
        change_anchor,
        change_new,
        1,
    )


# Substituir el controlador del mapa.
pattern = re.compile(
    r"  const selectLocationFromMap = \("
    r".*?"
    r"(?=  const toggleSearchLanguage = \()",
    re.DOTALL,
)

new_handler = """  const selectLocationFromMap = (
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

"""

app, count = pattern.subn(
    new_handler,
    app,
    count=1,
)

if count != 1:
    raise RuntimeError(
        "No s'ha pogut substituir "
        "selectLocationFromMap."
    )

app_path.write_text(
    app,
    encoding="utf-8",
)


print()
print(
    "Geocodificació inversa afegida "
    "correctament."
)
print()
