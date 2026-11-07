export type GeocodedLocation = {
  query: string
  display_name: string
  latitude: number
  longitude: number
  country_code: string
  location_name: string
  bounding_box?: number[] | null
}

type ApiErrorResponse = {
  detail?: string
}

const API_BASE_URL = 'http://127.0.0.1:8000'

export async function geocodeLocation(
  query: string,
  signal?: AbortSignal,
): Promise<GeocodedLocation> {
  const response = await fetch(
    `${API_BASE_URL}/geocode-location`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
      }),
      signal,
    },
  )

  if (!response.ok) {
    let message =
      `El localitzador ha retornat l’error ${response.status}.`

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

  return (await response.json()) as GeocodedLocation
}


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

