from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

OVERPASS_PATH = (
    ROOT
    / "apps"
    / "dashboard"
    / "src"
    / "services"
    / "overpass.ts"
)


def main():
    text = OVERPASS_PATH.read_text(
        encoding="utf-8"
    )

    # Eliminem la llista anterior de servidors
    old_endpoints = """const OVERPASS_ENDPOINTS = [
  'https://overpass.private.coffee/api/interpreter',
  'https://overpass-api.de/api/interpreter',
] as const
"""

    if old_endpoints in text:
        text = text.replace(
            old_endpoints,
            """const LOCAL_OVERPASS_ENDPOINT =
  'http://127.0.0.1:8000/overpass-query'
""",
            1,
        )

    # També permet aplicar-ho si encara quedava
    # l'endpoint original antic.
    old_single = """const OVERPASS_ENDPOINT =
  'https://overpass-api.de/api/interpreter'
"""

    if old_single in text:
        text = text.replace(
            old_single,
            """const LOCAL_OVERPASS_ENDPOINT =
  'http://127.0.0.1:8000/overpass-query'
""",
            1,
        )

    start = text.find(
        "async function executeOverpassQuery("
    )

    end_marker = "\nfunction degreesToRadians"

    end = text.find(
        end_marker,
        start,
    )

    if start < 0 or end < 0:
        raise RuntimeError(
            "No s'ha localitzat "
            "executeOverpassQuery."
        )

    new_function = r"""async function executeOverpassQuery(
  query: string,
  countryCode: string,
  signal?: AbortSignal,
): Promise<OverpassResponse> {
  const response = await fetch(
    LOCAL_OVERPASS_ENDPOINT,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        country_code: countryCode,
      }),
      signal,
    },
  )

  if (!response.ok) {
    let message =
      `El servei local d’Overpass ha retornat l’error ${response.status}.`

    try {
      const data = (await response.json()) as {
        detail?: string
      }

      if (data.detail) {
        message = data.detail
      }
    } catch {
      // Conservem el missatge genèric.
    }

    throw new Error(message)
  }

  return (await response.json()) as OverpassResponse
}
"""

    text = (
        text[:start]
        + new_function
        + text[end:]
    )

    old_call = """    await executeOverpassQuery(
      query,
      signal,
    )
"""

    new_call = """    await executeOverpassQuery(
      query,
      location.country_code,
      signal,
    )
"""

    if old_call not in text:
        raise RuntimeError(
            "No s'ha trobat la crida "
            "a executeOverpassQuery."
        )

    text = text.replace(
        old_call,
        new_call,
        1,
    )

    OVERPASS_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "Dashboard connectat al proxy local d'Overpass."
    )


if __name__ == "__main__":
    main()