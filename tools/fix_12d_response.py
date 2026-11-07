from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MAIN_PATH = (
    ROOT
    / "services"
    / "api"
    / "app"
    / "main.py"
)


def main() -> None:
    text = MAIN_PATH.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------
    # 1. Fer robust el model AnalyzeResponse
    # --------------------------------------------------

    text = text.replace(
        """    detected_language: str | None
    analysis_languages: list[str]
""",
        """    detected_language: str | None = None
    analysis_languages: list[str] = Field(
        default_factory=list,
    )
""",
        1,
    )

    # --------------------------------------------------
    # 2. Comprovar que la detecció 12D existeix
    # --------------------------------------------------

    analyze_start = text.find(
        "async def analyze_site("
    )

    if analyze_start < 0:
        raise RuntimeError(
            "No s'ha trobat analyze_site."
        )

    analyze_text = text[analyze_start:]

    if (
        "detected_language = detect_html_language("
        not in analyze_text
    ):
        raise RuntimeError(
            "La detecció d'idioma del Pas 12D "
            "no apareix dins analyze_site."
        )

    if (
        "analysis_languages = list("
        not in analyze_text
    ):
        raise RuntimeError(
            "No apareix analysis_languages "
            "dins analyze_site."
        )

    # --------------------------------------------------
    # 3. Reparar el return AnalyzeResponse final
    # --------------------------------------------------

    target = """            blocked_urls=blocked_urls,
        )
"""

    replacement = """            blocked_urls=blocked_urls,
            detected_language=detected_language,
            analysis_languages=analysis_languages,
        )
"""

    analyze_start = text.find(
        "async def analyze_site("
    )

    prefix = text[:analyze_start]
    analyze_text = text[analyze_start:]

    if (
        "detected_language=detected_language,"
        not in analyze_text
    ):
        position = analyze_text.rfind(target)

        if position < 0:
            raise RuntimeError(
                "No s'ha trobat el return final "
                "d'AnalyzeResponse."
            )

        analyze_text = (
            analyze_text[:position]
            + replacement
            + analyze_text[
                position + len(target):
            ]
        )

        text = prefix + analyze_text

    MAIN_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "Resposta del Pas 12D reparada correctament."
    )


if __name__ == "__main__":
    main()