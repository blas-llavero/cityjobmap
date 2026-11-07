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
    build_fallback_career_subdomain_candidates,
    same_site,
)


career_terms = (
    "careers",
    "jobs",
    "karriere",
    "stellen",
)

contact_terms = (
    "contact",
    "kontakt",
)


result = (
    build_fallback_career_subdomain_candidates(
        "https://www.example.org/",
        career_terms,
        contact_terms,
        [],
    )
)

print()
print("SUBDOMINIS GENERATS:")

for candidate in result:
    print(
        candidate.score,
        candidate.url,
    )


urls = {
    candidate.url
    for candidate in result
}

assert (
    "https://jobs.example.org/"
    in urls
)

assert (
    "https://careers.example.org/"
    in urls
)

assert len(result) <= 2


assert same_site(
    "https://example.org/",
    "https://jobs.example.org/",
)

assert same_site(
    "https://example.org/",
    "https://careers.example.org/",
)


# No generar jobs.jobs.example.org
already_jobs = (
    build_fallback_career_subdomain_candidates(
        "https://jobs.example.org/",
        career_terms,
        contact_terms,
        [],
    )
)

assert already_jobs == []


# No generar subdominis sobre un host profund.
deep_host = (
    build_fallback_career_subdomain_candidates(
        "https://portal.company.example.org/",
        career_terms,
        contact_terms,
        [],
    )
)

assert deep_host == []


print()
print(
    "Test 12E-B2 completat correctament."
)