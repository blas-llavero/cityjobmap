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

    old_endpoint = """const OVERPASS_ENDPOINT =
  'https://overpass-api.de/api/interpreter'
"""

    new_endpoints = """const OVERPASS_ENDPOINTS = [
  'https://overpass.private.coffee/api/interpreter',
  'https://overpass-api.de/api/interpreter',
] as const
"""

    if old_endpoint in text:
        text = text.replace(
            old_endpoint,
            new_endpoints,
            1,
        )

    old_function = """async function executeOverpassQuery(
  query: string,
  signal?: AbortSignal,
): Promise<OverpassResponse> {
  const response = await fetch(OVERPASS_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type':
        'application/x-www-form-urlencoded;charset=UTF-8',
    },
    body: new URLSearchParams({
      data: query,
    }),
    signal,
  })

  if (!response.ok) {
    throw new Error(
      `Overpass ha retornat l'error ${response.status}: ${response.statusText}`,
    )
  }

  return (await response.json()) as OverpassResponse
}
"""

    new_function = """async function executeOverpassQuery(
  query: string,
  signal?: AbortSignal,
): Promise<OverpassResponse> {
  const errors: string[] = []

  for (const endpoint of OVERPASS_ENDPOINTS) {
    if (signal?.aborted) {
      throw new DOMException(
        'Operació cancel·lada',
        'AbortError',
      )
    }

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/x-www-form-urlencoded;charset=UTF-8',
        },
        body: new URLSearchParams({
          data: query,
        }),
        signal,
      })

      if (response.ok) {
        return (await response.json()) as OverpassResponse
      }

      errors.push(
        `${endpoint}: ${response.status} ${response.statusText}`,
      )

      const retryableStatus = [
        429,
        500,
        502,
        503,
        504,
      ].includes(response.status)

      if (!retryableStatus) {
        throw new Error(
          `Overpass ha retornat l'error ${response.status}: ${response.statusText}`,
        )
      }
    } catch (error) {
      if (
        error instanceof DOMException &&
        error.name === 'AbortError'
      ) {
        throw error
      }

      if (error instanceof Error) {
        errors.push(
          `${endpoint}: ${error.message}`,
        )
      }
    }
  }

  throw new Error(
    `Cap servidor d'Overpass ha pogut completar la consulta. ${errors.join(' | ')}`,
  )
}
"""

    if old_function not in text:
        raise RuntimeError(
            "No s'ha trobat la funció "
            "executeOverpassQuery esperada."
        )

    text = text.replace(
        old_function,
        new_function,
        1,
    )

    OVERPASS_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "Failover d'Overpass afegit correctament."
    )


if __name__ == "__main__":
    main()