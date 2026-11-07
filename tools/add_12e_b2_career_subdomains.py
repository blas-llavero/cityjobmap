from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]

MAIN_PATH = (
    ROOT
    / "services"
    / "api"
    / "app"
    / "main.py"
)


HELPER = r'''
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


'''


def replace_once(
    text: str,
    old: str,
    new: str,
    description: str,
) -> str:
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"No s'ha pogut modificar "
            f"{description}. Coincidencies: {count}"
        )

    return text.replace(
        old,
        new,
        1,
    )


def main() -> None:
    text = MAIN_PATH.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------
    # 1. Afegir el generador de subdominis
    # --------------------------------------------------

    if (
        "def build_fallback_career_subdomain_candidates("
        not in text
    ):
        marker = (
            "def add_targeted_fallback_candidates("
        )

        position = text.find(marker)

        if position < 0:
            raise RuntimeError(
                "No s'ha trobat "
                "add_targeted_fallback_candidates()."
            )

        text = (
            text[:position]
            + HELPER
            + text[position:]
        )

    # --------------------------------------------------
    # 2. Afegir-los al mateix fallback de B1
    # --------------------------------------------------

    if (
        "subdomain_fallbacks = ("
        not in text
    ):
        old = '''    fallbacks = (
        build_fallback_career_candidates(
            home_url,
            languages,
            career_terms,
            contact_terms,
            candidates,
        )
    )

    merged: dict[str, CandidateLink] = {
'''

        new = '''    path_fallbacks = (
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
'''

        text = replace_once(
            text,
            old,
            new,
            "els candidats de subdomini",
        )

    # --------------------------------------------------
    # 3. Cada host ha d'utilitzar el SEU robots.txt
    # --------------------------------------------------

    if (
        "candidate_robots = robots"
        not in text
    ):
        old = '''        for candidate in candidates:
            if not robots.can_fetch(
                USER_AGENT,
                candidate.url,
            ):
                blocked_urls.append(
                    candidate.url
                )
                continue

            if crawl_delay > 0:
                await asyncio.sleep(
                    crawl_delay
                )

            try:
'''

        new = '''        for candidate in candidates:
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
'''

        text = replace_once(
            text,
            old,
            new,
            "robots.txt per host",
        )

    # --------------------------------------------------
    # 4. Validar Python abans d'escriure
    # --------------------------------------------------

    ast.parse(text)

    required = (
        "def build_fallback_career_subdomain_candidates(",
        "subdomain_fallbacks = (",
        "candidate_robots = robots",
        "candidate_crawl_delay",
    )

    for fragment in required:
        if fragment not in text:
            raise RuntimeError(
                f"Falta el fragment: {fragment}"
            )

    MAIN_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "12E-B2 aplicat correctament."
    )


if __name__ == "__main__":
    main()