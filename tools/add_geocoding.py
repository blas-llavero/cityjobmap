from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = ROOT / "services" / "api" / "app" / "main.py"


def replace_once(text, old, new, description):
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"No s'ha pogut aplicar {description}. "
            f"Coincidències trobades: {count}"
        )

    return text.replace(old, new, 1)


def main():
    text = MAIN_PATH.read_text(encoding="utf-8")

    # ---------------------------------------------------------
    # 1. Endpoint públic de Nominatim
    # ---------------------------------------------------------

    if "NOMINATIM_SEARCH_URL" not in text:
        text = replace_once(
            text,
            '''REQUEST_TIMEOUT_SECONDS = 12.0
''',
            '''REQUEST_TIMEOUT_SECONDS = 12.0

NOMINATIM_SEARCH_URL = (
    "https://nominatim.openstreetmap.org/search"
)
''',
            "la configuració de Nominatim",
        )

    # ---------------------------------------------------------
    # 2. Models de dades
    # ---------------------------------------------------------

    if "class GeocodeRequest" not in text:
        text = replace_once(
            text,
            '''class AnalyzeRequest(BaseModel):
''',
            '''class GeocodeRequest(BaseModel):
    query: str = Field(
        min_length=2,
        max_length=250,
    )


class GeocodeResponse(BaseModel):
    query: str
    display_name: str
    latitude: float
    longitude: float
    country_code: str
    location_name: str


class AnalyzeRequest(BaseModel):
''',
            "els models de geocodificació",
        )

    # ---------------------------------------------------------
    # 3. Endpoint /geocode-location
    # ---------------------------------------------------------

    if '@app.post("/geocode-location"' not in text:
        endpoint = r'''

@app.post(
    "/geocode-location",
    response_model=GeocodeResponse,
)
async def geocode_location(
    payload: GeocodeRequest,
) -> GeocodeResponse:
    query = payload.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="La ubicació és obligatòria.",
        )

    timeout = httpx.Timeout(
        REQUEST_TIMEOUT_SECONDS
    )

    try:
        async with httpx.AsyncClient(
            timeout=timeout
        ) as client:
            response = await client.get(
                NOMINATIM_SEARCH_URL,
                params={
                    "q": query,
                    "format": "jsonv2",
                    "limit": 1,
                    "addressdetails": 1,
                },
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/json",
                    "Accept-Language": (
                        "en,ca;q=0.9,es;q=0.8"
                    ),
                },
            )
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail=(
                "No s'ha pogut consultar "
                "el servei de localització."
            ),
        ) from error

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=(
                "El servei de localització "
                f"ha retornat l'error "
                f"{response.status_code}."
            ),
        )

    try:
        results = response.json()
    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail=(
                "El servei de localització "
                "ha retornat dades no vàlides."
            ),
        ) from error

    if not results:
        raise HTTPException(
            status_code=404,
            detail=(
                "No s'ha trobat aquesta ubicació. "
                "Prova d'afegir el país."
            ),
        )

    result = results[0]

    address = result.get("address") or {}

    country_code = str(
        address.get("country_code", "")
    ).lower()

    location_name = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or result.get("name")
        or query
    )

    try:
        latitude = float(result["lat"])
        longitude = float(result["lon"])
    except (KeyError, TypeError, ValueError) as error:
        raise HTTPException(
            status_code=502,
            detail=(
                "No s'han pogut obtenir "
                "les coordenades."
            ),
        ) from error

    return GeocodeResponse(
        query=query,
        display_name=str(
            result.get("display_name", query)
        ),
        latitude=latitude,
        longitude=longitude,
        country_code=country_code,
        location_name=str(location_name),
    )
'''

        marker = '@app.get("/health")'

        if marker not in text:
            raise RuntimeError(
                "No s'ha trobat l'endpoint /health."
            )

        text = text.replace(
            marker,
            endpoint + "\n\n" + marker,
            1,
        )

    MAIN_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "Geocodificació afegida correctament."
    )


if __name__ == "__main__":
    main()