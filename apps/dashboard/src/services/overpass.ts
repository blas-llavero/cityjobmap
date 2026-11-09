import type { GeocodedLocation } from './locationApi'
import { API_BASE_URL } from './apiConfig'

const OVERPASS_ENDPOINT =
  `${API_BASE_URL}/overpass-query`

const INITIAL_FALLBACK_RADIUS_KM = 6

type OverpassTags = Record<string, string>

type OverpassElement = {
  type: 'node' | 'way' | 'relation'
  id: number
  lat?: number
  lon?: number
  center?: {
    lat: number
    lon: number
  }
  tags?: OverpassTags
}

type OverpassResponse = {
  elements: OverpassElement[]
}

export type OrganizationResult = {
  id: string
  osmType: OverpassElement['type']
  osmId: number
  name: string
  municipality: string
  website: string | null
  email: string | null
  phone: string | null
  latitude: number | null
  longitude: number | null
  distanceKm: number | null
  category: string
  searchableText: string
}

type Coordinates = {
  latitude: number
  longitude: number
}

function buildOrganizationSelectors(
  locationFilter: string,
): string {
  return `
    nwr["name"]["office"]${locationFilter};
    nwr["name"]["amenity"~"school|college|university|training|research_institute"]${locationFilter};
    nwr["name"]["craft"~"electrician|electronics_repair"]${locationFilter};
    nwr["name"]["shop"~"computer|electronics"]${locationFilter};
    nwr["name"]["industrial"]${locationFilter};
    nwr["name"]["healthcare"="laboratory"]${locationFilter};
  `
}

async function executeOverpassQuery(
  query: string,
  countryCode: string,
  signal?: AbortSignal,
): Promise<OverpassResponse> {
  const response = await fetch(
    OVERPASS_ENDPOINT,
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

function degreesToRadians(
  degrees: number,
): number {
  return (degrees * Math.PI) / 180
}

function calculateDistanceKm(
  origin: Coordinates,
  destination: Coordinates,
): number {
  const earthRadiusKm = 6371

  const latitudeDifference =
    degreesToRadians(
      destination.latitude - origin.latitude,
    )

  const longitudeDifference =
    degreesToRadians(
      destination.longitude - origin.longitude,
    )

  const originLatitude =
    degreesToRadians(origin.latitude)

  const destinationLatitude =
    degreesToRadians(destination.latitude)

  const haversine =
    Math.sin(latitudeDifference / 2) ** 2 +
    Math.cos(originLatitude) *
      Math.cos(destinationLatitude) *
      Math.sin(longitudeDifference / 2) ** 2

  const angularDistance =
    2 *
    Math.atan2(
      Math.sqrt(haversine),
      Math.sqrt(1 - haversine),
    )

  return (
    Math.round(
      earthRadiusKm *
        angularDistance *
        10,
    ) / 10
  )
}

function normalizeWebsite(
  tags: OverpassTags,
): string | null {
  const website =
    tags.website ??
    tags['contact:website']

  if (!website) {
    return null
  }

  if (
    website.startsWith('https://') ||
    website.startsWith('http://')
  ) {
    return website
  }

  return `https://${website}`
}

function detectCategory(
  tags: OverpassTags,
): string {
  if (tags.amenity === 'school') {
    return 'Centre educatiu'
  }

  if (tags.amenity === 'college') {
    return 'Centre de formació'
  }

  if (tags.amenity === 'university') {
    return 'Universitat'
  }

  if (tags.amenity === 'training') {
    return 'Centre de formació'
  }

  if (
    tags.amenity === 'research_institute'
  ) {
    return 'Centre de recerca'
  }

  if (
    tags.healthcare === 'laboratory'
  ) {
    return 'Laboratori'
  }

  if (tags.craft === 'electrician') {
    return 'Empresa d’electricitat'
  }

  if (
    tags.craft === 'electronics_repair'
  ) {
    return 'Electrònica'
  }

  if (tags.shop === 'computer') {
    return 'Informàtica'
  }

  if (tags.shop === 'electronics') {
    return 'Electrònica'
  }

  if (tags.office) {
    return `Oficina: ${tags.office}`
  }

  if (tags.industrial) {
    return `Empresa industrial: ${tags.industrial}`
  }

  return 'Organització'
}

function buildSearchableText(
  tags: OverpassTags,
): string {
  return Object.entries(tags)
    .map(
      ([key, value]) =>
        `${key} ${value}`,
    )
    .join(' ')
}

function convertElement(
  element: OverpassElement,
  searchCenter: Coordinates,
  fallbackMunicipality: string,
): OrganizationResult | null {
  const tags = element.tags

  if (!tags?.name) {
    return null
  }

  const latitude =
    element.lat ??
    element.center?.lat ??
    null

  const longitude =
    element.lon ??
    element.center?.lon ??
    null

  const distanceKm =
    latitude !== null &&
    longitude !== null
      ? calculateDistanceKm(
          searchCenter,
          {
            latitude,
            longitude,
          },
        )
      : null

  return {
    id: `${element.type}-${element.id}`,
    osmType: element.type,
    osmId: element.id,
    name: tags.name,
    municipality:
      tags['addr:city'] ??
      tags['addr:municipality'] ??
      tags['addr:town'] ??
      tags['addr:village'] ??
      fallbackMunicipality,
    website: normalizeWebsite(tags),
    email:
      tags.email ??
      tags['contact:email'] ??
      null,
    phone:
      tags.phone ??
      tags['contact:phone'] ??
      null,
    latitude,
    longitude,
    distanceKm,
    category: detectCategory(tags),
    searchableText:
      buildSearchableText(tags),
  }
}

function removeDuplicates(
  organizations: OrganizationResult[],
): OrganizationResult[] {
  const uniqueOrganizations =
    new Map<string, OrganizationResult>()

  for (const organization of organizations) {
    const normalizedName =
      organization.name
        .trim()
        .toLocaleLowerCase()

    const normalizedWebsite =
      organization.website
        ?.trim()
        .toLocaleLowerCase() ?? ''

    const key = normalizedWebsite
      ? `${normalizedName}|${normalizedWebsite}`
      : `${normalizedName}|${organization.latitude}|${organization.longitude}`

    if (!uniqueOrganizations.has(key)) {
      uniqueOrganizations.set(
        key,
        organization,
      )
    }
  }

  return [
    ...uniqueOrganizations.values(),
  ].sort((first, second) => {
    const firstDistance =
      first.distanceKm ??
      Number.POSITIVE_INFINITY

    const secondDistance =
      second.distanceKm ??
      Number.POSITIVE_INFINITY

    if (
      firstDistance !== secondDistance
    ) {
      return (
        firstDistance -
        secondDistance
      )
    }

    return first.name.localeCompare(
      second.name,
    )
  })
}

function getInitialLocationFilter(
  location: GeocodedLocation,
): string {
  const bounds = location.bounding_box

  if (
    bounds &&
    bounds.length === 4 &&
    bounds.every(Number.isFinite)
  ) {
    const [
      south,
      north,
      west,
      east,
    ] = bounds

    return `(${south},${west},${north},${east})`
  }

  const fallbackRadiusMeters =
    INITIAL_FALLBACK_RADIUS_KM * 1000

  return (
    `(around:${fallbackRadiusMeters},` +
    `${location.latitude},` +
    `${location.longitude})`
  )
}

function getRadiusLocationFilter(
  location: GeocodedLocation,
  radiusKm: number,
): string {
  const radiusMeters =
    Math.round(radiusKm * 1000)

  return (
    `(around:${radiusMeters},` +
    `${location.latitude},` +
    `${location.longitude})`
  )
}

async function searchLocation(
  location: GeocodedLocation,
  radiusKm: number,
  signal?: AbortSignal,
): Promise<OrganizationResult[]> {
  const searchCenter: Coordinates = {
    latitude: location.latitude,
    longitude: location.longitude,
  }

  const locationFilter =
    radiusKm === 0
      ? getInitialLocationFilter(location)
      : getRadiusLocationFilter(
          location,
          radiusKm,
        )

  const selectors =
    buildOrganizationSelectors(
      locationFilter,
    )

  const query = `
    [out:json][timeout:35];

    (
      ${selectors}
    );

    out center tags;
  `

  const data =
    await executeOverpassQuery(
      query,
      location.country_code,
      signal,
    )

  return removeDuplicates(
    data.elements
      .map((element) =>
        convertElement(
          element,
          searchCenter,
          location.location_name,
        ),
      )
      .filter(
        (
          organization,
        ): organization is OrganizationResult =>
          organization !== null,
      ),
  )
}

export async function searchOrganizations(
  location: GeocodedLocation,
  radiusKm: number,
  signal?: AbortSignal,
): Promise<OrganizationResult[]> {
  if (
    !Number.isFinite(
      location.latitude,
    ) ||
    !Number.isFinite(
      location.longitude,
    )
  ) {
    throw new Error(
      'La ubicació de cerca no és vàlida.',
    )
  }

  if (
    !Number.isFinite(radiusKm) ||
    radiusKm < 0
  ) {
    throw new Error(
      'El radi de cerca no és vàlid.',
    )
  }

  return searchLocation(
    location,
    radiusKm,
    signal,
  )
}