import { useEffect, useRef } from 'react'
import {
  Map,
  Marker,
  NavigationControl,
  setWorkerUrl,
  type MapMouseEvent,
} from 'maplibre-gl'

import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import 'maplibre-gl/dist/maplibre-gl.css'
import './LocationMap.css'

setWorkerUrl(workerUrl)

type LocationMapProps = {
  latitude?: number | null
  longitude?: number | null
  onSelect: (
    latitude: number,
    longitude: number,
  ) => void
}

export function LocationMap({
  latitude,
  longitude,
  onSelect,
}: LocationMapProps) {
  const containerRef =
    useRef<HTMLDivElement | null>(null)

  const mapRef =
    useRef<Map | null>(null)

  const markerRef =
    useRef<Marker | null>(null)

  useEffect(() => {
    if (!containerRef.current) {
      return
    }

    const hasSelectedPoint =
      latitude != null &&
      longitude != null

    const map = new Map({
      container: containerRef.current,
      style:
        'https://tiles.openfreemap.org/styles/liberty',
      center: hasSelectedPoint
        ? [longitude, latitude]
        : [0, 20],
      zoom: hasSelectedPoint ? 11 : 1.5,
    })

    map.addControl(
      new NavigationControl(),
      'top-right',
    )

    map.on(
      'click',
      (event: MapMouseEvent) => {
        const selectedLongitude =
          event.lngLat.lng

        const selectedLatitude =
          event.lngLat.lat

        markerRef.current?.remove()

        markerRef.current = new Marker()
          .setLngLat([
            selectedLongitude,
            selectedLatitude,
          ])
          .addTo(map)

        onSelect(
          selectedLatitude,
          selectedLongitude,
        )
      },
    )

    if (hasSelectedPoint) {
      markerRef.current = new Marker()
        .setLngLat([
          longitude,
          latitude,
        ])
        .addTo(map)
    }

    mapRef.current = map

    return () => {
      markerRef.current?.remove()
      markerRef.current = null

      map.remove()
      mapRef.current = null
    }
  }, [])

  useEffect(() => {
    const map = mapRef.current

    if (
      !map ||
      latitude == null ||
      longitude == null
    ) {
      return
    }

    markerRef.current?.remove()

    markerRef.current = new Marker()
      .setLngLat([
        longitude,
        latitude,
      ])
      .addTo(map)

    map.flyTo({
      center: [
        longitude,
        latitude,
      ],
      zoom: Math.max(
        map.getZoom(),
        10,
      ),
    })
  }, [
    latitude,
    longitude,
  ])

  return (
    <div className="location-map-wrapper">
      <div
        ref={containerRef}
        className="location-map"
        aria-label="Mapa per seleccionar la ubicació"
      />

      <p className="location-map-help">
        Clica qualsevol punt del mapa per utilitzar-lo
        com a centre de la cerca.
      </p>
    </div>
  )
}