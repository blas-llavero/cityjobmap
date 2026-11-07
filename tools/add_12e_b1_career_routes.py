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

    for language in languages:
        for path in (
            FALLBACK_CAREER_PATHS_BY_LANGUAGE.get(
                language,
                (),
            )
        ):
            if path not in paths:
                paths.append(path)

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

    fallbacks = (
        build_fallback_career_candidates(
            home_url,
            languages,
            career_terms,
            contact_terms,
            candidates,
        )
    )

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


'''


def main() -> None:
    text = MAIN_PATH.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------
    # 1. Afegir helpers abans de page_text()
    # --------------------------------------------

    if (
        "def add_targeted_fallback_candidates("
        not in text
    ):
        marker = "def page_text(html: str) -> str:"

        position = text.find(marker)

        if position < 0:
            raise RuntimeError(
                "No s'ha trobat page_text()."
            )

        text = (
            text[:position]
            + HELPER
            + text[position:]
        )

    # --------------------------------------------
    # 2. AST: trobar exactament
    #    candidates = extract_candidate_links(...)
    #    dins analyze_site()
    # --------------------------------------------

    if (
        "candidates = add_targeted_fallback_candidates("
        not in text
    ):
        tree = ast.parse(text)

        analyze_function = None

        for node in ast.walk(tree):
            if (
                isinstance(
                    node,
                    ast.AsyncFunctionDef,
                )
                and node.name == "analyze_site"
            ):
                analyze_function = node
                break

        if analyze_function is None:
            raise RuntimeError(
                "No s'ha trobat analyze_site()."
            )

        target_assignment = None

        for node in ast.walk(
            analyze_function
        ):
            if not isinstance(
                node,
                ast.Assign,
            ):
                continue

            has_candidates_target = any(
                isinstance(target, ast.Name)
                and target.id == "candidates"
                for target in node.targets
            )

            calls_extract = (
                isinstance(node.value, ast.Call)
                and isinstance(
                    node.value.func,
                    ast.Name,
                )
                and node.value.func.id
                == "extract_candidate_links"
            )

            if (
                has_candidates_target
                and calls_extract
            ):
                target_assignment = node
                break

        if target_assignment is None:
            raise RuntimeError(
                "No s'ha trobat "
                "candidates = "
                "extract_candidate_links(...)."
            )

        if (
            target_assignment.end_lineno
            is None
        ):
            raise RuntimeError(
                "AST no ha retornat end_lineno."
            )

        lines = text.splitlines(
            keepends=True
        )

        source_line = lines[
            target_assignment.lineno - 1
        ]

        indentation = source_line[
            : len(source_line)
            - len(source_line.lstrip())
        ]

        insertion = [
            "\n",
            (
                indentation
                + "candidates = "
                + "add_targeted_fallback_candidates(\n"
            ),
            (
                indentation
                + "    candidates,\n"
            ),
            (
                indentation
                + "    final_home_url,\n"
            ),
            (
                indentation
                + "    analysis_languages,\n"
            ),
            (
                indentation
                + "    career_terms,\n"
            ),
            (
                indentation
                + "    contact_terms,\n"
            ),
            (
                indentation
                + ")\n"
            ),
        ]

        insertion_index = (
            target_assignment.end_lineno
        )

        lines[
            insertion_index:
            insertion_index
        ] = insertion

        text = "".join(lines)

    # --------------------------------------------
    # 3. Validació abans de guardar
    # --------------------------------------------

    ast.parse(text)

    if (
        "def add_targeted_fallback_candidates("
        not in text
    ):
        raise RuntimeError(
            "Falten els helpers 12E-B1."
        )

    if (
        "candidates = add_targeted_fallback_candidates("
        not in text
    ):
        raise RuntimeError(
            "El 12E-B1 no està connectat "
            "amb analyze_site()."
        )

    MAIN_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "12E-B1 aplicat correctament."
    )


if __name__ == "__main__":
    main()