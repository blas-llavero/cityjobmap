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
    # 1. Ampliar AnalyzeResponse
    # --------------------------------------------------

    old_model = '''class AnalyzeResponse(BaseModel):
    website: str
    final_home_url: str
    status: Status
    status_label: str
    career_url: str | None
    contact_url: str | None
    pages_checked: list[str]
    evidence: list[Evidence]
    blocked_urls: list[str]
'''

    new_model = '''class AnalyzeResponse(BaseModel):
    website: str
    final_home_url: str
    status: Status
    status_label: str
    career_url: str | None
    contact_url: str | None
    pages_checked: list[str]
    evidence: list[Evidence]
    blocked_urls: list[str]
    detected_language: str | None
    analysis_languages: list[str]
'''

    if old_model in text:
        text = replace_once(
            text,
            old_model,
            new_model,
            "AnalyzeResponse",
        )

    # --------------------------------------------------
    # 2. Detector d'idioma declarat
    # --------------------------------------------------

    if "def detect_html_language(" not in text:
        marker = '''def normalize_analysis_languages(
'''

        helper = r'''def normalize_detected_language(
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


'''

        if marker not in text:
            raise RuntimeError(
                "No s'ha trobat "
                "normalize_analysis_languages."
            )

        text = text.replace(
            marker,
            helper + marker,
            1,
        )

    # --------------------------------------------------
    # 3. Detectar idioma després de descarregar la home
    # --------------------------------------------------

    old_home = '''        home_html = require_small_text_response(
            response,
            final_home_url,
            (
                "text/html",
                "application/xhtml+xml",
            ),
        )

        candidates = extract_candidate_links(
'''

    new_home = '''        home_html = require_small_text_response(
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
'''

    if old_home in text:
        text = replace_once(
            text,
            old_home,
            new_home,
            "detecció automàtica d'idioma",
        )
    elif "detected_language = detect_html_language(" not in text:
        raise RuntimeError(
            "No s'ha trobat el bloc home_html."
        )

    # --------------------------------------------------
    # 4. Resposta robots.txt
    # --------------------------------------------------

    old_blocked = '''                blocked_urls=[start_url],
            )
'''

    new_blocked = '''                blocked_urls=[start_url],
                detected_language=None,
                analysis_languages=languages,
            )
'''

    if old_blocked in text:
        text = replace_once(
            text,
            old_blocked,
            new_blocked,
            "resposta robots.txt",
        )

    # --------------------------------------------------
    # 5. Resposta final
    # --------------------------------------------------

    old_final = '''            blocked_urls=blocked_urls,
        )
'''

    new_final = '''            blocked_urls=blocked_urls,
            detected_language=detected_language,
            analysis_languages=analysis_languages,
        )
'''

    if old_final in text:
        text = replace_once(
            text,
            old_final,
            new_final,
            "resposta final de l'anàlisi",
        )

    MAIN_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "Detecció automàtica d'idioma "
        "afegida a FastAPI."
    )


if __name__ == "__main__":
    main()