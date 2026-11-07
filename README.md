# CityJobMap

**Find jobs and opportunities on the map.**

CityJobMap is an open-source web application for discovering organisations,
companies and educational institutions around a selected geographic location
and identifying potential employment opportunities.

## Main features

- Select a search location by city or municipality name.
- Select an exact point directly on an interactive map.
- Reverse geocoding of map locations.
- Search progressively by geographic radius.
- Discover nearby organisations using OpenStreetMap data.
- Analyse organisation websites for employment and career information.
- Search using different professional profiles.

## Current professional profiles

- Bioinformatics
- Information technology
- Cybersecurity
- Mathematics teaching
- IT teaching
- Technology teaching
- Electricity teaching
- Electronics teaching

## Technology

### Frontend

- React
- TypeScript
- Vite
- MapLibre GL JS
- OpenFreeMap

### Backend

- Python
- FastAPI
- httpx
- Beautiful Soup

### Geographic data and services

- OpenStreetMap
- Nominatim
- Overpass API

## Development

### Backend

Run from the project root:

    & ".\services\api\.venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir ".\services\api" --host 127.0.0.1 --port 8000 --reload

### Frontend

Run from the project root:

    pnpm dev

The development frontend is available at:

    http://localhost:5173

## License

CityJobMap is free and open-source software licensed under the
GNU Affero General Public License version 3.

See the LICENSE file.

Third-party libraries and services retain their respective licenses
and terms of use.

## Author

Conceived and programmed by **Blas Llavero**.