from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(
        ROOT
        / "services"
        / "api"
    ),
)

from app.main import (
    CandidateLink,
    add_targeted_fallback_candidates,
)


def show(
    title,
    candidates,
):
    print()
    print(title)

    for candidate in candidates:
        print(
            candidate.score,
            candidate.url,
        )


# --------------------------------------------------
# CAS 1
# Alemany + només contacte descobert.
# Ha d'afegir rutes laborals probables.
# --------------------------------------------------

existing = [
    CandidateLink(
        url="https://example.org/kontakt",
        label="Kontakt",
        score=5,
    )
]

result = add_targeted_fallback_candidates(
    existing,
    "https://example.org/de.html",
    ["en", "de"],
    (
        "careers",
        "jobs",
        "karriere",
        "stellen",
        "stellenangebote",
    ),
    (
        "contact",
        "kontakt",
    ),
)

show(
    "CAS 1 - fallbacks:",
    result,
)

urls = {
    candidate.url
    for candidate in result
}

assert (
    "https://example.org/careers"
    in urls
    or
    "https://example.org/jobs"
    in urls
    or
    "https://example.org/karriere"
    in urls
)

assert len(result) <= 7


# --------------------------------------------------
# CAS 2
# Ja existeix un enllaç Careers real.
# NO ha d'inventar més rutes.
# --------------------------------------------------

existing_career = [
    CandidateLink(
        url="https://example.org/company/careers",
        label="Careers",
        score=20,
    )
]

result_career = (
    add_targeted_fallback_candidates(
        existing_career,
        "https://example.org/",
        ["en"],
        (
            "careers",
            "jobs",
        ),
        (
            "contact",
        ),
    )
)

show(
    "CAS 2 - enllac real:",
    result_career,
)

assert len(result_career) == 1

assert (
    result_career[0].url
    ==
    "https://example.org/company/careers"
)

print()
print(
    "Test 12E-B1 completat correctament."
)