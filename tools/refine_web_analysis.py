from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = ROOT / "services" / "api" / "app" / "main.py"


def replace_once(
    text: str,
    old: str,
    new: str,
    description: str,
) -> str:
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"No s'ha pogut aplicar {description}. "
            f"Coincidències trobades: {count}"
        )

    return text.replace(old, new, 1)


def main() -> None:
    text = MAIN_PATH.read_text(encoding="utf-8")

    if "NON_JOB_TERMS" not in text:
        text = replace_once(
            text,
            '''STRONG_OFFER_TERMS = (
    "we are hiring",
''',
            '''NON_JOB_TERMS = (
    "empren",
    "emprenedoria",
    "emprendimiento",
    "entrepreneurship",
    "entrepreneur",
    "creacio d empreses",
    "creacion de empresas",
)

STRONG_OFFER_TERMS = (
    "we are hiring",
''',
            "la llista d'exclusions",
        )

    old_function = '''def link_score(
    label: str,
    url: str,
) -> int:
    normalized = normalize_text(
        f"{label} {url}"
    )

    score = 0

    for term in CAREER_TERMS:
        if normalize_text(term) in normalized:
            score += 10

    for term in CONTACT_TERMS:
        if normalize_text(term) in normalized:
            score += 5

    return score
'''

    new_function = '''def link_score(
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

    if old_function in text:
        text = text.replace(
            old_function,
            new_function,
            1,
        )

    MAIN_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print("Filtre de falsos positius aplicat correctament.")


if __name__ == "__main__":
    main()