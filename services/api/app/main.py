from __future__ import annotations

import asyncio
import ipaddress
import re
import socket
import unicodedata
from dataclasses import dataclass
from typing import Literal
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


APP_NAME = "CityJobMap API"

USER_AGENT = (
    "CityJobMap/0.1 "
    "(local open-source job research tool)"
)

MAX_PAGES = 8
MAX_BYTES = 2_000_000
MAX_REDIRECTS = 5
REQUEST_TIMEOUT_SECONDS = 12.0

NOMINATIM_SEARCH_URL = (
    "https://nominatim.openstreetmap.org/search"
)



NOMINATIM_REVERSE_URL = (
    "https://nominatim.openstreetmap.org/reverse"
)
SUPPORTED_ANALYSIS_LANGUAGES = {
    "en",
    "de",
    "fr",
    "it",
    "ca",
    "es",
}


CAREER_TERMS_BY_LANGUAGE = {
    "en": (
        "careers",
        "career",
        "jobs",
        "job",
        "job openings",
        "open positions",
        "vacancies",
        "vacancy",
        "work with us",
        "join us",
        "join our team",
        "employment",
        "opportunities",
        "talent",
    ),

    "de": (
        "karriere",
        "jobs",
        "stellen",
        "stellenangebote",
        "stellenangebot",
        "offene stellen",
        "offene positionen",
        "arbeiten bei uns",
        "arbeiten sie bei uns",
        "bewerbung",
        "bewerben",
        "jobangebote",
        "vakanz",
        "vakanzen",
    ),

    "fr": (
        "carrières",
        "carriere",
        "carrière",
        "emplois",
        "emploi",
        "offres d'emploi",
        "offre d'emploi",
        "postes vacants",
        "poste vacant",
        "recrutement",
        "rejoignez-nous",
        "rejoindre notre équipe",
        "opportunités",
    ),

    "it": (
        "carriere",
        "carriera",
        "lavora con noi",
        "lavoro",
        "offerte di lavoro",
        "offerta di lavoro",
        "posizioni aperte",
        "posizione aperta",
        "opportunità di lavoro",
        "opportunita di lavoro",
        "unisciti a noi",
        "candidatura",
    ),

    "ca": (
        "treballa amb nosaltres",
        "treballa amb nosaltres",
        "ofertes de feina",
        "oferta de feina",
        "ofertes de treball",
        "oferta de treball",
        "vacants",
        "vacant",
        "feina",
        "incorpora't",
        "incorporat",
        "uneix-te a l'equip",
    ),

    "es": (
        "trabaja con nosotros",
        "trabaja con nosotros",
        "ofertas de empleo",
        "oferta de empleo",
        "ofertas de trabajo",
        "oferta de trabajo",
        "vacantes",
        "vacante",
        "empleo",
        "únete al equipo",
        "unete al equipo",
        "oportunidades laborales",
    ),
}


CONTACT_TERMS_BY_LANGUAGE = {
    "en": (
        "contact",
        "contact us",
        "get in touch",
    ),

    "de": (
        "kontakt",
        "kontaktieren",
        "kontaktieren sie uns",
        "ansprechpartner",
    ),

    "fr": (
        "contact",
        "contactez-nous",
        "nous contacter",
    ),

    "it": (
        "contatti",
        "contatto",
        "contattaci",
    ),

    "ca": (
        "contacte",
        "contacta",
        "contacta amb nosaltres",
    ),

    "es": (
        "contacto",
        "contacta",
        "contacta con nosotros",
    ),
}


NON_JOB_TERMS = (
    "empren",
    "emprenedoria",
    "emprendimiento",
    "entrepreneurship",
    "entrepreneur",
    "creacio d empreses",
    "creacion de empresas",
)

STRONG_OFFER_TERMS_BY_LANGUAGE = {
    "en": (
        "we are hiring",
        "now hiring",
        "open positions",
        "current vacancies",
        "job openings",
        "apply now",
    ),

    "de": (
        "wir suchen",
        "wir stellen ein",
        "offene stellen",
        "aktuelle stellenangebote",
        "jetzt bewerben",
        "bewerben sie sich",
    ),

    "fr": (
        "nous recrutons",
        "poste à pourvoir",
        "postes à pourvoir",
        "offres d'emploi",
        "offres d’emploi",
        "postulez",
    ),

    "it": (
        "stiamo assumendo",
        "posizioni aperte",
        "offerte di lavoro",
        "candidati ora",
        "cerchiamo",
    ),

    "ca": (
        "estem buscant",
        "busquem",
        "ofertes de feina",
        "oferta de treball",
        "vacant disponible",
        "presenta la teva candidatura",
    ),

    "es": (
        "estamos buscando",
        "buscamos",
        "ofertas de empleo",
        "oferta de trabajo",
        "vacante disponible",
        "envía tu candidatura",
        "envia tu candidatura",
    ),
}


Status = Literal[
    "possible_active_offer",
    "careers_page",
    "contact_page",
    "website_only",
    "robots_blocked",
]


class GeocodeRequest(BaseModel):
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
    bounding_box: list[float] | None = None


class OverpassRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=50000,
    )

    country_code: str | None = Field(
        default=None,
        max_length=2,
    )


class AnalyzeRequest(BaseModel):
    website: str = Field(
        min_length=1,
        max_length=2048,
    )

    languages: list[str] = Field(
        default_factory=lambda: ["en"],
    )


class Evidence(BaseModel):
    kind: Literal["offer", "careers", "contact"]
    label: str
    url: str
    excerpt: str | None = None


class AnalyzeResponse(BaseModel):
    website: str
    final_home_url: str
    status: Status
    status_label: str
    career_url: str | None
    contact_url: str | None
    pages_checked: list[str]
    evidence: list[Evidence]
    blocked_urls: list[str]
    detected_language: str | None = None
    analysis_languages: list[str] = Field(
        default_factory=list,
    )


@dataclass(frozen=True)
class CandidateLink:
    url: str
    label: str
    score: int


app = FastAPI(
    title=APP_NAME,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def normalize_detected_language(
    value: str | None,
) -> str | None:
    if not value:
        return None

    candidates = re.split(
        r"[,;\s]+",
        value.strip().lower(),
    )

    for candidate in candidates:
        if not candidate:
            continue

        code = (
            candidate
            .split("-", 1)[0]
            .split("_", 1)[0]
        )

        if code in SUPPORTED_ANALYSIS_LANGUAGES:
            return code

    return None


def detect_html_language(
    html: str,
    content_language_header: str | None = None,
) -> str | None:
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    html_element = soup.find("html")

    if html_element is not None:
        declared_language = (
            html_element.get("lang")
        )

        detected = normalize_detected_language(
            str(declared_language)
            if declared_language
            else None
        )

        if detected:
            return detected

    content_language_meta = soup.find(
        "meta",
        attrs={
            "http-equiv": re.compile(
                r"^content-language$",
                re.IGNORECASE,
            )
        },
    )

    if content_language_meta is not None:
        detected = normalize_detected_language(
            str(
                content_language_meta.get(
                    "content",
                    "",
                )
            )
        )

        if detected:
            return detected

    language_meta = soup.find(
        "meta",
        attrs={
            "name": re.compile(
                r"^language$",
                re.IGNORECASE,
            )
        },
    )

    if language_meta is not None:
        detected = normalize_detected_language(
            str(
                language_meta.get(
                    "content",
                    "",
                )
            )
        )

        if detected:
            return detected

    return normalize_detected_language(
        content_language_header
    )



TEXT_LANGUAGE_MARKERS = {
    "en": {
        "jobs": 4,
        "careers": 4,
        "employment": 4,
        "vacancies": 4,
        "contact": 2,
        "about": 2,
        "company": 2,
        "work": 2,
        "team": 2,
        "the": 1,
        "and": 1,
        "with": 1,
    },
    "de": {
        "karriere": 4,
        "stellen": 4,
        "stellenangebote": 5,
        "bewerbung": 4,
        "kontakt": 2,
        "unternehmen": 2,
        "arbeiten": 2,
        "mitarbeiter": 2,
        "und": 1,
        "der": 1,
        "die": 1,
        "das": 1,
        "mit": 1,
    },
    "fr": {
        "carriere": 4,
        "carrieres": 4,
        "emploi": 4,
        "emplois": 4,
        "recrutement": 5,
        "contact": 2,
        "entreprise": 2,
        "equipe": 2,
        "travailler": 2,
        "les": 1,
        "des": 1,
        "avec": 1,
        "et": 1,
    },
    "it": {
        "carriera": 4,
        "carriere": 4,
        "lavoro": 4,
        "lavora": 4,
        "candidatura": 4,
        "contatti": 2,
        "azienda": 2,
        "squadra": 2,
        "opportunita": 3,
        "con": 1,
        "del": 1,
        "della": 1,
    },
    "ca": {
        "feina": 4,
        "feines": 4,
        "treballa": 4,
        "candidatura": 4,
        "contacte": 2,
        "empresa": 2,
        "equip": 2,
        "oportunitats": 3,
        "amb": 1,
        "els": 1,
        "les": 1,
    },
    "es": {
        "empleo": 4,
        "empleos": 4,
        "trabaja": 4,
        "vacantes": 4,
        "candidatura": 4,
        "contacto": 2,
        "empresa": 2,
        "equipo": 2,
        "oportunidades": 3,
        "con": 1,
        "los": 1,
        "las": 1,
    },
}


def normalize_language_detection_text(
    text: str,
) -> str:
    replacements = str.maketrans({
        "á": "a",
        "à": "a",
        "ä": "a",
        "â": "a",
        "ã": "a",
        "å": "a",
        "é": "e",
        "è": "e",
        "ë": "e",
        "ê": "e",
        "í": "i",
        "ì": "i",
        "ï": "i",
        "î": "i",
        "ó": "o",
        "ò": "o",
        "ö": "o",
        "ô": "o",
        "õ": "o",
        "ú": "u",
        "ù": "u",
        "ü": "u",
        "û": "u",
        "ç": "c",
        "ñ": "n",
        "ß": "ss",
    })

    return (
        text.casefold()
        .translate(replacements)
    )


def detect_text_language(
    html: str,
) -> str | None:
    """
    Detector textual conservador.

    S'utilitza nomes si HTML, meta i headers
    no declaren cap idioma reconegut.
    """
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    for removable in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
        ]
    ):
        removable.decompose()

    visible_text = soup.get_text(
        " ",
        strip=True,
    )

    normalized = (
        normalize_language_detection_text(
            visible_text
        )
    )[:30000]

    words = re.findall(
        r"[a-z]+",
        normalized,
    )

    if len(words) < 15:
        return None

    word_counts: dict[str, int] = {}

    for word in words:
        word_counts[word] = (
            word_counts.get(word, 0)
            + 1
        )

    scores: dict[str, int] = {}

    for language, markers in (
        TEXT_LANGUAGE_MARKERS.items()
    ):
        score = 0

        for marker, weight in markers.items():
            normalized_marker = (
                normalize_language_detection_text(
                    marker
                )
            )

            occurrences = min(
                word_counts.get(
                    normalized_marker,
                    0,
                ),
                6,
            )

            score += occurrences * weight

        scores[language] = score

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    if not ranked:
        return None

    best_language, best_score = ranked[0]

    second_score = (
        ranked[1][1]
        if len(ranked) > 1
        else 0
    )

    if best_score < 6:
        return None

    if best_score - second_score < 3:
        return None

    if (
        best_language
        not in SUPPORTED_ANALYSIS_LANGUAGES
    ):
        return None

    return best_language


def normalize_analysis_languages(
    languages: list[str],
) -> list[str]:
    normalized: list[str] = []

    for language in languages:
        code = language.strip().lower()

        if (
            code in SUPPORTED_ANALYSIS_LANGUAGES
            and code not in normalized
        ):
            normalized.append(code)

    if not normalized:
        return ["en"]

    return normalized


def terms_for_languages(
    terms_by_language: dict[
        str,
        tuple[str, ...],
    ],
    languages: list[str],
) -> tuple[str, ...]:
    result: list[str] = []

    for language in languages:
        for term in terms_by_language.get(
            language,
            (),
        ):
            if term not in result:
                result.append(term)

    return tuple(result)


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)

    without_diacritics = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )

    return re.sub(
        r"\s+",
        " ",
        without_diacritics.lower(),
    ).strip()


def normalize_start_url(raw_url: str) -> str:
    value = raw_url.strip()

    if not value:
        raise HTTPException(
            status_code=400,
            detail="La web és obligatòria.",
        )

    if "://" not in value:
        value = f"https://{value}"

    parsed = urlparse(value)

    return urlunparse(
        parsed._replace(fragment="")
    )


def ensure_public_http_url(url: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(
            status_code=400,
            detail="Només s'admeten webs HTTP o HTTPS.",
        )

    if not parsed.hostname:
        raise HTTPException(
            status_code=400,
            detail="La web no té un domini vàlid.",
        )

    if parsed.username or parsed.password:
        raise HTTPException(
            status_code=400,
            detail="No s'admeten credencials dins de la URL.",
        )

    if parsed.port not in {None, 80, 443}:
        raise HTTPException(
            status_code=400,
            detail="Només s'admeten els ports web 80 i 443.",
        )

    try:
        address_info = socket.getaddrinfo(
            parsed.hostname,
            parsed.port
            or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as error:
        raise HTTPException(
            status_code=400,
            detail="No s'ha pogut resoldre el domini.",
        ) from error

    addresses = {
        ipaddress.ip_address(item[4][0])
        for item in address_info
    }

    if not addresses:
        raise HTTPException(
            status_code=400,
            detail="El domini no té una adreça accessible.",
        )

    if any(not address.is_global for address in addresses):
        raise HTTPException(
            status_code=400,
            detail=(
                "La web apunta a una adreça privada "
                "o no permesa."
            ),
        )


async def safe_get(
    client: httpx.AsyncClient,
    url: str,
) -> tuple[httpx.Response, str]:
    current_url = url

    for _ in range(MAX_REDIRECTS + 1):
        ensure_public_http_url(current_url)

        try:
            response = await client.get(
                current_url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": (
                        "text/html,"
                        "text/plain;q=0.9,"
                        "*/*;q=0.1"
                    ),
                },
                follow_redirects=False,
            )
        except httpx.HTTPError as error:
            raise HTTPException(
                status_code=502,
                detail=(
                    "No s'ha pogut consultar "
                    f"{current_url}."
                ),
            ) from error

        if response.status_code in {
            301,
            302,
            303,
            307,
            308,
        }:
            location = response.headers.get("location")

            if not location:
                raise HTTPException(
                    status_code=502,
                    detail=(
                        "La web ha retornat una "
                        "redirecció sense destinació."
                    ),
                )

            current_url = urljoin(
                current_url,
                location,
            )

            continue

        return response, current_url

    raise HTTPException(
        status_code=502,
        detail=(
            "La web ha superat el nombre "
            "màxim de redireccions."
        ),
    )


def require_small_text_response(
    response: httpx.Response,
    url: str,
    allowed_types: tuple[str, ...],
) -> str:
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=(
                f"La web ha retornat l'error "
                f"{response.status_code} a {url}."
            ),
        )

    content_type = response.headers.get(
        "content-type",
        "",
    ).lower()

    if content_type and not any(
        allowed_type in content_type
        for allowed_type in allowed_types
    ):
        raise HTTPException(
            status_code=415,
            detail=(
                f"El recurs {url} no és "
                "text HTML compatible."
            ),
        )

    if len(response.content) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"El recurs {url} supera "
                "la mida màxima permesa."
            ),
        )

    return response.text


async def load_robots(
    client: httpx.AsyncClient,
    home_url: str,
) -> tuple[RobotFileParser, float]:
    parsed = urlparse(home_url)

    root = (
        f"{parsed.scheme}://"
        f"{parsed.netloc}"
    )

    robots_url = urljoin(
        root,
        "/robots.txt",
    )

    parser = RobotFileParser()
    parser.set_url(robots_url)

    try:
        response, final_url = await safe_get(
            client,
            robots_url,
        )
    except HTTPException:
        parser.parse([])
        return parser, 0.0

    if response.status_code == 404:
        parser.parse([])
        return parser, 0.0

    try:
        text = require_small_text_response(
            response,
            final_url,
            (
                "text/plain",
                "text/html",
            ),
        )
    except HTTPException:
        parser.parse([])
        return parser, 0.0

    parser.parse(text.splitlines())

    delay = (
        parser.crawl_delay(USER_AGENT)
        or parser.crawl_delay("*")
        or 0.0
    )

    return parser, min(
        max(float(delay), 0.0),
        10.0,
    )


def same_site(
    base_url: str,
    candidate_url: str,
) -> bool:
    base_host = (
        urlparse(base_url).hostname or ""
    ).lower()

    candidate_host = (
        urlparse(candidate_url).hostname or ""
    ).lower()

    return (
        candidate_host == base_host
        or candidate_host.endswith(
            f".{base_host}"
        )
        or base_host.endswith(
            f".{candidate_host}"
        )
    )


def link_score(
    label: str,
    url: str,
    career_terms: tuple[str, ...],
    contact_terms: tuple[str, ...],
) -> int:
    normalized = normalize_text(
        f"{label} {url}"
    )

    if any(
        normalize_text(term) in normalized
        for term in NON_JOB_TERMS
    ):
        return 0

    score = 0

    for term in career_terms:
        if normalize_text(term) in normalized:
            score += 10

    for term in contact_terms:
        if normalize_text(term) in normalized:
            score += 5

    return score


def extract_candidate_links(
    html: str,
    page_url: str,
    career_terms: tuple[str, ...],
    contact_terms: tuple[str, ...],
) -> list[CandidateLink]:
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    candidates: dict[
        str,
        CandidateLink,
    ] = {}

    for anchor in soup.find_all(
        "a",
        href=True,
    ):
        raw_href = str(
            anchor.get("href", "")
        ).strip()

        if not raw_href:
            continue

        if raw_href.startswith(
            (
                "#",
                "mailto:",
                "tel:",
                "javascript:",
            )
        ):
            continue

        absolute_url = urljoin(
            page_url,
            raw_href,
        )

        parsed = urlparse(absolute_url)

        clean_url = urlunparse(
            parsed._replace(fragment="")
        )

        if parsed.scheme not in {
            "http",
            "https",
        }:
            continue

        if not same_site(
            page_url,
            clean_url,
        ):
            continue

        label = " ".join(
            anchor.stripped_strings
        ).strip()

        score = link_score(
            label,
            clean_url,
            career_terms,
            contact_terms,
        )

        if score <= 0:
            continue

        candidate = CandidateLink(
            url=clean_url,
            label=label or clean_url,
            score=score,
        )

        existing = candidates.get(
            clean_url
        )

        if (
            existing is None
            or candidate.score > existing.score
        ):
            candidates[clean_url] = candidate

    return sorted(
        candidates.values(),
        key=lambda candidate: (
            -candidate.score,
            candidate.url,
        ),
    )[: MAX_PAGES - 1]



MAX_FALLBACK_CAREER_PROBES = 4


FALLBACK_CAREER_PATHS_UNIVERSAL = (
    "/careers",
    "/jobs",
)


FALLBACK_CAREER_PATHS_BY_LANGUAGE = {
    "en": (
        "/career",
        "/job-openings",
        "/open-positions",
        "/join-us",
        "/join-our-team",
        "/work-with-us",
    ),

    "de": (
        "/karriere",
        "/stellen",
        "/stellenangebote",
        "/jobs-karriere",
        "/arbeiten-bei-uns",
    ),

    "fr": (
        "/carrieres",
        "/carriere",
        "/emplois",
        "/emploi",
        "/recrutement",
        "/nous-rejoindre",
    ),

    "it": (
        "/lavora-con-noi",
        "/lavoro",
        "/carriere",
        "/carriera",
        "/posizioni-aperte",
    ),

    "ca": (
        "/treballa-amb-nosaltres",
        "/feina",
        "/feines",
        "/ofertes-de-feina",
    ),

    "es": (
        "/trabaja-con-nosotros",
        "/empleo",
        "/empleos",
        "/vacantes",
        "/ofertas-de-empleo",
    ),
}


def candidate_contains_career_term(
    candidate: CandidateLink,
    career_terms: tuple[str, ...],
) -> bool:
    normalized = normalize_text(
        f"{candidate.label} {candidate.url}"
    )

    return any(
        normalize_text(term) in normalized
        for term in career_terms
    )


def build_fallback_career_candidates(
    home_url: str,
    languages: list[str],
    career_terms: tuple[str, ...],
    contact_terms: tuple[str, ...],
    existing_candidates: list[CandidateLink],
) -> list[CandidateLink]:
    """
    Genera unes poques rutes laborals probables
    del MATEIX host.

    No fa cap peticio HTTP aqui.
    Només crea candidats que el crawler normal
    comprovara després amb robots.txt, safe_get,
    límits de mida i resta de proteccions.
    """
    parsed = urlparse(home_url)

    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
    ):
        return []

    origin = (
        f"{parsed.scheme}://{parsed.netloc}"
    )

    paths: list[str] = []

    for path in FALLBACK_CAREER_PATHS_UNIVERSAL:
        if path not in paths:
            paths.append(path)

    # Repartim les places restants entre
    # els idiomes en lloc d'esgotar primer
    # totes les rutes del primer idioma.
    language_order = list(
        dict.fromkeys(languages)
    )

    language_path_lists = [
        list(
            FALLBACK_CAREER_PATHS_BY_LANGUAGE.get(
                language,
                (),
            )
        )
        for language in language_order
    ]

    path_index = 0

    while (
        len(paths)
        < MAX_FALLBACK_CAREER_PROBES
    ):
        added_in_round = False

        for language_paths in language_path_lists:
            if path_index >= len(language_paths):
                continue

            path = language_paths[path_index]

            if path not in paths:
                paths.append(path)
                added_in_round = True

            if (
                len(paths)
                >= MAX_FALLBACK_CAREER_PROBES
            ):
                break

        if not added_in_round:
            break

        path_index += 1

    existing_urls = {
        candidate.url
        for candidate in existing_candidates
    }

    result: list[CandidateLink] = []

    for path in paths:
        url = f"{origin}{path}"

        if url in existing_urls:
            continue

        score = link_score(
            path,
            url,
            career_terms,
            contact_terms,
        )

        # Les rutes conegudes són una pista forta,
        # però menys fiable que un enllaç real
        # descobert a la portada.
        score = max(
            14,
            score + 4,
        )

        result.append(
            CandidateLink(
                url=url,
                label=(
                    "Ruta laboral probable "
                    f"{path}"
                ),
                score=score,
            )
        )

        if (
            len(result)
            >= MAX_FALLBACK_CAREER_PROBES
        ):
            break

    return result



MAX_FALLBACK_CAREER_SUBDOMAIN_PROBES = 2


FALLBACK_CAREER_SUBDOMAIN_PREFIXES = (
    "jobs",
    "careers",
)


def build_fallback_career_subdomain_candidates(
    home_url: str,
    career_terms: tuple[str, ...],
    contact_terms: tuple[str, ...],
    existing_candidates: list[CandidateLink],
) -> list[CandidateLink]:
    """
    Genera com a maxim dos subdominis laborals
    previsibles.

    Exemples:
        jobs.example.org
        careers.example.org

    Aquesta funcio NO fa peticions HTTP.
    """
    parsed = urlparse(home_url)

    host = (
        parsed.hostname or ""
    ).lower().strip(".")

    if not host:
        return []

    if host.startswith("www."):
        host = host[4:]

    if host.startswith(
        (
            "jobs.",
            "careers.",
        )
    ):
        return []

    # Evitem generar subdominis sobre hosts
    # que ja semblen subdominis profunds.
    #
    # example.com       -> correcte
    # example.ch        -> correcte
    # example.co.uk     -> correcte
    # portal.example.com -> no provar
    if len(host.split(".")) > 3:
        return []

    scheme = (
        parsed.scheme
        if parsed.scheme in {"http", "https"}
        else "https"
    )

    base_origin = (
        f"{scheme}://{host}"
    )

    existing_urls = {
        candidate.url.rstrip("/")
        for candidate in existing_candidates
    }

    result: list[CandidateLink] = []

    for prefix in (
        FALLBACK_CAREER_SUBDOMAIN_PREFIXES
    ):
        url = (
            f"{scheme}://"
            f"{prefix}.{host}/"
        )

        if (
            url.rstrip("/")
            in existing_urls
        ):
            continue

        if not same_site(
            base_origin,
            url,
        ):
            continue

        score = link_score(
            prefix,
            url,
            career_terms,
            contact_terms,
        )

        score = max(
            13,
            score + 3,
        )

        result.append(
            CandidateLink(
                url=url,
                label=(
                    "Subdomini laboral probable "
                    f"{prefix}.{host}"
                ),
                score=score,
            )
        )

        if (
            len(result)
            >=
            MAX_FALLBACK_CAREER_SUBDOMAIN_PROBES
        ):
            break

    return result


def add_targeted_fallback_candidates(
    candidates: list[CandidateLink],
    home_url: str,
    languages: list[str],
    career_terms: tuple[str, ...],
    contact_terms: tuple[str, ...],
) -> list[CandidateLink]:
    """
    Només prova rutes predictibles quan
    la portada NO ens ha proporcionat ja
    un enllaç laboral clar.
    """
    has_career_candidate = any(
        candidate_contains_career_term(
            candidate,
            career_terms,
        )
        for candidate in candidates
    )

    if has_career_candidate:
        return candidates

    path_fallbacks = (
        build_fallback_career_candidates(
            home_url,
            languages,
            career_terms,
            contact_terms,
            candidates,
        )
    )

    subdomain_fallbacks = (
        build_fallback_career_subdomain_candidates(
            home_url,
            career_terms,
            contact_terms,
            candidates,
        )
    )

    fallbacks = [
        *path_fallbacks,
        *subdomain_fallbacks,
    ]

    merged: dict[str, CandidateLink] = {
        candidate.url: candidate
        for candidate in candidates
    }

    for candidate in fallbacks:
        existing = merged.get(
            candidate.url
        )

        if (
            existing is None
            or candidate.score > existing.score
        ):
            merged[candidate.url] = candidate

    return sorted(
        merged.values(),
        key=lambda candidate: (
            -candidate.score,
            candidate.url,
        ),
    )[: MAX_PAGES - 1]


def page_text(html: str) -> str:
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    for element in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
        ]
    ):
        element.decompose()

    return normalize_text(
        " ".join(soup.stripped_strings)
    )


def find_first_term(
    text: str,
    terms: tuple[str, ...],
) -> str | None:
    for term in terms:
        if normalize_text(term) in text:
            return term

    return None


def excerpt_for_term(
    text: str,
    term: str,
    size: int = 180,
) -> str:
    normalized_term = normalize_text(term)

    position = text.find(
        normalized_term
    )

    if position < 0:
        return ""

    start = max(
        0,
        position - size // 2,
    )

    end = min(
        len(text),
        position
        + len(normalized_term)
        + size // 2,
    )

    excerpt = text[start:end].strip()

    if start > 0 or end < len(text):
        return f"…{excerpt}…"

    return excerpt




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

    raw_bounding_box = result.get("boundingbox")

    bounding_box = None

    if (
        isinstance(raw_bounding_box, list)
        and len(raw_bounding_box) == 4
    ):
        try:
            bounding_box = [
                float(raw_bounding_box[0]),
                float(raw_bounding_box[1]),
                float(raw_bounding_box[2]),
                float(raw_bounding_box[3]),
            ]
        except (TypeError, ValueError):
            bounding_box = None

    return GeocodeResponse(
        query=query,
        display_name=str(
            result.get("display_name", query)
        ),
        latitude=latitude,
        longitude=longitude,
        country_code=country_code,
        location_name=str(location_name),
        bounding_box=bounding_box,
    )



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


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": APP_NAME,
    }


@app.post(
    "/analyze-site",
    response_model=AnalyzeResponse,
)
async def analyze_site(
    payload: AnalyzeRequest,
) -> AnalyzeResponse:
    start_url = normalize_start_url(
        payload.website
    )

    ensure_public_http_url(start_url)

    languages = normalize_analysis_languages(
        payload.languages
    )

    career_terms = terms_for_languages(
        CAREER_TERMS_BY_LANGUAGE,
        languages,
    )

    contact_terms = terms_for_languages(
        CONTACT_TERMS_BY_LANGUAGE,
        languages,
    )

    strong_offer_terms = terms_for_languages(
        STRONG_OFFER_TERMS_BY_LANGUAGE,
        languages,
    )

    timeout = httpx.Timeout(
        REQUEST_TIMEOUT_SECONDS
    )

    async with httpx.AsyncClient(
        timeout=timeout
    ) as client:
        robots, crawl_delay = await load_robots(
            client,
            start_url,
        )

        if not robots.can_fetch(
            USER_AGENT,
            start_url,
        ):
            return AnalyzeResponse(
                website=payload.website,
                final_home_url=start_url,
                status="robots_blocked",
                status_label=(
                    "Anàlisi bloquejada per robots.txt"
                ),
                career_url=None,
                contact_url=None,
                pages_checked=[],
                evidence=[],
                blocked_urls=[start_url],
                detected_language=None,
                analysis_languages=languages,
            )

        response, final_home_url = await safe_get(
            client,
            start_url,
        )

        home_html = require_small_text_response(
            response,
            final_home_url,
            (
                "text/html",
                "application/xhtml+xml",
            ),
        )

        detected_language = detect_html_language(
            home_html,
            response.headers.get(
                "content-language"
            ),
        )

        if not detected_language:
            detected_language = detect_text_language(
                home_html,
            )

        analysis_languages = list(
            languages
        )

        if (
            detected_language
            and detected_language
            not in analysis_languages
        ):
            analysis_languages.append(
                detected_language
            )

        career_terms = terms_for_languages(
            CAREER_TERMS_BY_LANGUAGE,
            analysis_languages,
        )

        contact_terms = terms_for_languages(
            CONTACT_TERMS_BY_LANGUAGE,
            analysis_languages,
        )

        strong_offer_terms = terms_for_languages(
            STRONG_OFFER_TERMS_BY_LANGUAGE,
            analysis_languages,
        )

        candidates = extract_candidate_links(
            home_html,
            final_home_url,
            career_terms,
            contact_terms,
        )

        fallback_languages = list(
            analysis_languages
        )

        if (
            detected_language
            and detected_language
            in fallback_languages
        ):
            fallback_languages = [
                detected_language,
                *[
                    language
                    for language
                    in fallback_languages
                    if language
                    != detected_language
                ],
            ]

        candidates = add_targeted_fallback_candidates(
            candidates,
            final_home_url,
            fallback_languages,
            career_terms,
            contact_terms,
        )

        pages: list[
            tuple[str, str, str]
        ] = [
            (
                final_home_url,
                "Pàgina principal",
                home_html,
            )
        ]

        blocked_urls: list[str] = []

        for candidate in candidates:
            candidate_robots = robots
            candidate_crawl_delay = (
                crawl_delay
            )

            home_host = (
                urlparse(
                    final_home_url
                ).hostname
                or ""
            ).lower()

            candidate_host = (
                urlparse(
                    candidate.url
                ).hostname
                or ""
            ).lower()

            # Un subdomini pot tenir una politica
            # robots.txt diferent del domini principal.
            if (
                candidate_host
                and candidate_host
                != home_host
            ):
                try:
                    (
                        candidate_robots,
                        candidate_crawl_delay,
                    ) = await load_robots(
                        client,
                        candidate.url,
                    )
                except HTTPException:
                    continue

            if not candidate_robots.can_fetch(
                USER_AGENT,
                candidate.url,
            ):
                blocked_urls.append(
                    candidate.url
                )
                continue

            if candidate_crawl_delay > 0:
                await asyncio.sleep(
                    candidate_crawl_delay
                )

            try:
                (
                    candidate_response,
                    final_candidate_url,
                ) = await safe_get(
                    client,
                    candidate.url,
                )

                candidate_html = (
                    require_small_text_response(
                        candidate_response,
                        final_candidate_url,
                        (
                            "text/html",
                            "application/xhtml+xml",
                        ),
                    )
                )
            except HTTPException:
                continue

            pages.append(
                (
                    final_candidate_url,
                    candidate.label,
                    candidate_html,
                )
            )

        evidence: list[Evidence] = []

        career_url: str | None = None
        contact_url: str | None = None

        for url, label, html in pages:
            text = page_text(html)

            combined = normalize_text(
                f"{label} {url} {text[:6000]}"
            )

            offer_term = find_first_term(
                combined,
                strong_offer_terms,
            )

            career_term = find_first_term(
                normalize_text(
                    f"{label} {url}"
                ),
                career_terms,
            )

            contact_term = find_first_term(
                normalize_text(
                    f"{label} {url}"
                ),
                contact_terms,
            )

            if offer_term:
                evidence.append(
                    Evidence(
                        kind="offer",
                        label=(
                            "Possible oferta: "
                            f"{offer_term}"
                        ),
                        url=url,
                        excerpt=excerpt_for_term(
                            text,
                            offer_term,
                        ),
                    )
                )

            if (
                career_term
                and career_url is None
            ):
                career_url = url

                evidence.append(
                    Evidence(
                        kind="careers",
                        label=(
                            "Pàgina de feina: "
                            f"{label}"
                        ),
                        url=url,
                    )
                )

            if (
                contact_term
                and contact_url is None
            ):
                contact_url = url

                evidence.append(
                    Evidence(
                        kind="contact",
                        label=(
                            "Pàgina de contacte: "
                            f"{label}"
                        ),
                        url=url,
                    )
                )

        has_offer = any(
            item.kind == "offer"
            for item in evidence
        )

        if has_offer:
            status: Status = (
                "possible_active_offer"
            )

            status_label = (
                "Possible oferta activa: "
                "revisió manual necessària"
            )

        elif career_url:
            status = "careers_page"

            status_label = (
                "Pàgina de feina o "
                "treballa amb nosaltres"
            )

        elif contact_url:
            status = "contact_page"

            status_label = (
                "Contacte disponible per "
                "candidatura espontània"
            )

        else:
            status = "website_only"

            status_label = (
                "Web disponible, sense "
                "pàgina laboral detectada"
            )

        return AnalyzeResponse(
            website=payload.website,
            final_home_url=final_home_url,
            status=status,
            status_label=status_label,
            career_url=career_url,
            contact_url=contact_url,
            pages_checked=[
                url
                for url, _, _ in pages
            ],
            evidence=evidence,
            blocked_urls=blocked_urls,
            detected_language=detected_language,
            analysis_languages=analysis_languages,
        )


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

