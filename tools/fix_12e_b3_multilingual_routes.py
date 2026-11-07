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
    # 1. Repartir les rutes entre els idiomes
    # --------------------------------------------------

    old_paths = '''    paths: list[str] = []

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
'''

    new_paths = '''    paths: list[str] = []

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
'''

    if old_paths in text:
        text = replace_once(
            text,
            old_paths,
            new_paths,
            "l'ordre multilingue de les rutes",
        )
    elif "language_path_lists = [" not in text:
        raise RuntimeError(
            "No s'ha trobat el bloc de rutes "
            "del 12E-B1."
        )

    # --------------------------------------------------
    # 2. Prioritzar l'idioma detectat a la web
    # --------------------------------------------------

    old_call = '''        candidates = add_targeted_fallback_candidates(
            candidates,
            final_home_url,
            analysis_languages,
            career_terms,
            contact_terms,
        )
'''

    new_call = '''        fallback_languages = list(
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
'''

    if old_call in text:
        text = replace_once(
            text,
            old_call,
            new_call,
            "la prioritat de l'idioma detectat",
        )
    elif "fallback_languages = list(" not in text:
        raise RuntimeError(
            "No s'ha trobat la connexio "
            "del 12E-B1 amb analyze_site."
        )

    ast.parse(text)

    MAIN_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "12E-B3 aplicat correctament."
    )


if __name__ == "__main__":
    main()