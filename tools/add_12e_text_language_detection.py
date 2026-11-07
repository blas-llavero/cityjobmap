from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

MAIN_PATH = (
    ROOT
    / "services"
    / "api"
    / "app"
    / "main.py"
)


HELPER = r'''
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
    Fallback conservador.

    Només s'utilitza quan la web no declara
    cap idioma mitjançant HTML, meta o headers.
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
    )

    # No cal analitzar una pàgina enorme.
    normalized = normalized[:30000]

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

    for (
        language,
        markers,
    ) in TEXT_LANGUAGE_MARKERS.items():
        score = 0

        for marker, weight in markers.items():
            occurrences = min(
                word_counts.get(
                    normalize_language_detection_text(
                        marker
                    ),
                    0,
                ),
                6,
            )

            score += (
                occurrences
                * weight
            )

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

    # Preferim no decidir abans que endevinar malament.
    if best_score < 6:
        return None

    if (
        best_score - second_score
        < 3
    ):
        return None

    if (
        best_language
        not in SUPPORTED_ANALYSIS_LANGUAGES
    ):
        return None

    return best_language


'''


def main() -> None:
    text = MAIN_PATH.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------
    # 1. Afegir el detector textual
    # --------------------------------------------------

    if (
        "def detect_text_language("
        not in text
    ):
        marker = (
            "def normalize_analysis_languages("
        )

        position = text.find(marker)

        if position < 0:
            raise RuntimeError(
                "No s'ha trobat "
                "normalize_analysis_languages."
            )

        text = (
            text[:position]
            + HELPER
            + text[position:]
        )

    # --------------------------------------------------
    # 2. Afegir el fallback després del detector 12D
    # --------------------------------------------------

    if (
        "detected_language = detect_text_language("
        not in text
    ):
        pattern = re.compile(
            r'''(?P<indent>[ \t]*)detected_language\s*=\s*'''
            r'''detect_html_language\(\s*'''
            r'''home_html,\s*'''
            r'''response\.headers\.get\(\s*'''
            r'''["']content-language["']\s*'''
            r'''\),\s*'''
            r'''\)\s*''',
            re.MULTILINE,
        )

        match = pattern.search(text)

        if not match:
            raise RuntimeError(
                "No s'ha trobat la crida "
                "detect_html_language dins analyze_site."
            )

        original = match.group(0)
        indentation = match.group("indent")

        replacement = (
            original
            + "\n"
            + indentation
            + "if not detected_language:\n"
            + indentation
            + "    detected_language = "
            + "detect_text_language(\n"
            + indentation
            + "        home_html,\n"
            + indentation
            + "    )\n"
        )

        text = (
            text[:match.start()]
            + replacement
            + text[match.end():]
        )

    MAIN_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "12E-A aplicat: "
        "deteccio textual d'idioma disponible."
    )


if __name__ == "__main__":
    main()