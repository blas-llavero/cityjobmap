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
    text: str,
    old: str,
    new: str,
    description: str,
) -> str:
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"No s'ha pogut aplicar «{description}». "
            f"Coincidències: {count}"
        )

    return text.replace(old, new, 1)


def main() -> None:
    text = MAIN_PATH.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------
    # 1. Diccionaris multilingües
    # --------------------------------------------------

    if "CAREER_TERMS_BY_LANGUAGE" not in text:
        marker = "CAREER_TERMS = ("

        start = text.find(marker)

        if start < 0:
            raise RuntimeError(
                "No s'ha trobat CAREER_TERMS."
            )

        end_marker = "\n\nCONTACT_TERMS = ("
        end = text.find(end_marker, start)

        if end < 0:
            raise RuntimeError(
                "No s'ha trobat CONTACT_TERMS."
            )

        new_career_terms = r'''SUPPORTED_ANALYSIS_LANGUAGES = {
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
'''

        text = (
            text[:start]
            + new_career_terms
            + text[end:]
        )

    # --------------------------------------------------
    # 2. CONTACT_TERMS
    # --------------------------------------------------

    if "CONTACT_TERMS_BY_LANGUAGE" not in text:
        start = text.find("CONTACT_TERMS = (")

        if start < 0:
            raise RuntimeError(
                "No s'ha trobat CONTACT_TERMS."
            )

        # El següent bloc pot ser NON_JOB_TERMS
        # o STRONG_OFFER_TERMS segons la versió.
        possible_markers = [
            "\n\nNON_JOB_TERMS = (",
            "\n\nSTRONG_OFFER_TERMS = (",
        ]

        end = -1

        for marker in possible_markers:
            candidate = text.find(marker, start)

            if candidate >= 0:
                if end < 0 or candidate < end:
                    end = candidate

        if end < 0:
            raise RuntimeError(
                "No s'ha trobat el final de CONTACT_TERMS."
            )

        replacement = r'''CONTACT_TERMS_BY_LANGUAGE = {
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
'''

        text = (
            text[:start]
            + replacement
            + text[end:]
        )

    # --------------------------------------------------
    # 3. STRONG_OFFER_TERMS
    # --------------------------------------------------

    if "STRONG_OFFER_TERMS_BY_LANGUAGE" not in text:
        start = text.find(
            "STRONG_OFFER_TERMS = ("
        )

        if start < 0:
            raise RuntimeError(
                "No s'ha trobat STRONG_OFFER_TERMS."
            )

        # Busquem el final de la tupla.
        end = text.find("\n)\n", start)

        if end < 0:
            raise RuntimeError(
                "No s'ha trobat el final de "
                "STRONG_OFFER_TERMS."
            )

        end += len("\n)\n")

        replacement = r'''STRONG_OFFER_TERMS_BY_LANGUAGE = {
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
'''

        text = (
            text[:start]
            + replacement
            + text[end:]
        )

    # --------------------------------------------------
    # 4. Helper per combinar idiomes
    # --------------------------------------------------

    if "def terms_for_languages(" not in text:
        marker = "def normalize_text(value: str) -> str:"

        helper = r'''def normalize_analysis_languages(
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


'''

        if marker not in text:
            raise RuntimeError(
                "No s'ha trobat normalize_text."
            )

        text = text.replace(
            marker,
            helper + marker,
            1,
        )

    # --------------------------------------------------
    # 5. AnalyzeRequest.languages
    # --------------------------------------------------

    old_model = '''class AnalyzeRequest(BaseModel):
    website: str = Field(min_length=1, max_length=2048)
'''

    new_model = '''class AnalyzeRequest(BaseModel):
    website: str = Field(
        min_length=1,
        max_length=2048,
    )

    languages: list[str] = Field(
        default_factory=lambda: ["en"],
    )
'''

    if old_model in text:
        text = replace_once(
            text,
            old_model,
            new_model,
            "AnalyzeRequest.languages",
        )

    elif (
        "class AnalyzeRequest" in text
        and "languages: list[str]" not in text[
            text.find("class AnalyzeRequest"):
            text.find("class Evidence")
        ]
    ):
        raise RuntimeError(
            "AnalyzeRequest té una estructura "
            "diferent de l'esperada."
        )

    # --------------------------------------------------
    # 6. link_score multilingüe
    # --------------------------------------------------

    old_link_score = '''def link_score(
    label: str,
    url: str,
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

    for term in CAREER_TERMS:
        if normalize_text(term) in normalized:
            score += 10

    for term in CONTACT_TERMS:
        if normalize_text(term) in normalized:
            score += 5

    return score
'''

    new_link_score = '''def link_score(
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
'''

    if old_link_score in text:
        text = replace_once(
            text,
            old_link_score,
            new_link_score,
            "link_score multilingüe",
        )

    # --------------------------------------------------
    # 7. extract_candidate_links multilingüe
    # --------------------------------------------------

    old_signature = '''def extract_candidate_links(
    html: str,
    page_url: str,
) -> list[CandidateLink]:
'''

    new_signature = '''def extract_candidate_links(
    html: str,
    page_url: str,
    career_terms: tuple[str, ...],
    contact_terms: tuple[str, ...],
) -> list[CandidateLink]:
'''

    if old_signature in text:
        text = replace_once(
            text,
            old_signature,
            new_signature,
            "extract_candidate_links",
        )

    old_score_call = '''        score = link_score(
            label,
            clean_url,
        )
'''

    new_score_call = '''        score = link_score(
            label,
            clean_url,
            career_terms,
            contact_terms,
        )
'''

    if old_score_call in text:
        text = replace_once(
            text,
            old_score_call,
            new_score_call,
            "crida a link_score",
        )

    # --------------------------------------------------
    # 8. Construir termes dins analyze_site
    # --------------------------------------------------

    marker = '''    start_url = normalize_start_url(
        payload.website
    )

    ensure_public_http_url(start_url)
'''

    replacement = '''    start_url = normalize_start_url(
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
'''

    if (
        marker in text
        and "strong_offer_terms = terms_for_languages" not in text[
            text.find("async def analyze_site"):
        ]
    ):
        text = replace_once(
            text,
            marker,
            replacement,
            "termes multilingües d'analyze_site",
        )

    # --------------------------------------------------
    # 9. Passar termes a extract_candidate_links
    # --------------------------------------------------

    old_candidates = '''        candidates = extract_candidate_links(
            home_html,
            final_home_url,
        )
'''

    new_candidates = '''        candidates = extract_candidate_links(
            home_html,
            final_home_url,
            career_terms,
            contact_terms,
        )
'''

    if old_candidates in text:
        text = replace_once(
            text,
            old_candidates,
            new_candidates,
            "termes dels enllaços candidats",
        )

    # --------------------------------------------------
    # 10. Substituir constants dins el bucle
    # --------------------------------------------------

    text = text.replace(
        '''                STRONG_OFFER_TERMS,
''',
        '''                strong_offer_terms,
''',
    )

    text = text.replace(
        '''                CAREER_TERMS,
''',
        '''                career_terms,
''',
    )

    text = text.replace(
        '''                CONTACT_TERMS,
''',
        '''                contact_terms,
''',
    )

    MAIN_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "FastAPI multilingüe actualitzat correctament."
    )


if __name__ == "__main__":
    main()