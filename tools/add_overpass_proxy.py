from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MAIN_PATH = (
    ROOT
    / "services"
    / "api"
    / "app"
    / "main.py"
)


def replace_once(
    text,
    old,
    new,
    description,
):
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"No s'ha pogut aplicar "
            f"{description}. Coincidències: {count}"
        )

    return text.replace(
        old,
        new,
        1,
    )


def main():
    text = MAIN_PATH.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------
    # Model de la petició
    # --------------------------------------------

    if "class OverpassRequest" not in text:
        marker = """class AnalyzeRequest(BaseModel):
"""

        model = """class OverpassRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=50000,
    )

    country_code: str | None = Field(
        default=None,
        max_length=2,
    )


"""

        text = replace_once(
            text,
            marker,
            model + marker,
            "el model OverpassRequest",
        )

    # --------------------------------------------
    # Endpoint local d'Overpass
    # --------------------------------------------

    if '@app.post("/overpass-query")' not in text:
        marker = """@app.get("/health")
"""

        endpoint = r'''
@app.post("/overpass-query")
async def overpass_query(
    payload: OverpassRequest,
):
    country_code = (
        payload.country_code
        or ""
    ).strip().lower()

    global_endpoints = [
        (
            "Private.coffee",
            "https://overpass.private.coffee/api/interpreter",
        ),
        (
            "Overpass principal",
            "https://overpass-api.de/api/interpreter",
        ),
    ]

    if country_code == "ch":
        endpoints = [
            (
                "Overpass Suïssa",
                "https://overpass.osm.ch/api/interpreter",
            ),
            *global_endpoints,
        ]
    else:
        endpoints = global_endpoints

    errors: list[str] = []

    timeout = httpx.Timeout(
        connect=12.0,
        read=70.0,
        write=20.0,
        pool=12.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout
    ) as client:
        for name, endpoint in endpoints:
            try:
                response = await client.post(
                    endpoint,
                    data={
                        "data": payload.query,
                    },
                    headers={
                        "User-Agent": USER_AGENT,
                        "Accept": "application/json",
                    },
                )
            except httpx.HTTPError as error:
                errors.append(
                    f"{name}: error de connexió "
                    f"({type(error).__name__})"
                )
                continue

            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError:
                    errors.append(
                        f"{name}: resposta JSON no vàlida"
                    )
                    continue

            errors.append(
                f"{name}: HTTP "
                f"{response.status_code} "
                f"{response.reason_phrase}"
            )

            if response.status_code not in {
                429,
                500,
                502,
                503,
                504,
            }:
                break

    raise HTTPException(
        status_code=502,
        detail=(
            "Cap servidor d'Overpass ha pogut "
            "completar la consulta. "
            + " | ".join(errors)
        ),
    )


'''

        text = replace_once(
            text,
            marker,
            endpoint + marker,
            "l'endpoint /overpass-query",
        )

    MAIN_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "Proxy local d'Overpass creat correctament."
    )


if __name__ == "__main__":
    main()