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


def get_status_value(call: ast.Call) -> str | None:
    for keyword in call.keywords:
        if keyword.arg != "status":
            continue

        if isinstance(keyword.value, ast.Constant):
            if isinstance(keyword.value.value, str):
                return keyword.value.value

    return None


def main() -> None:
    text = MAIN_PATH.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------
    # 1. Fer el model tolerant per seguretat
    # --------------------------------------------------

    old_model_fields = """    detected_language: str | None
    analysis_languages: list[str]
"""

    new_model_fields = """    detected_language: str | None = None
    analysis_languages: list[str] = Field(
        default_factory=list,
    )
"""

    if old_model_fields in text:
        text = text.replace(
            old_model_fields,
            new_model_fields,
            1,
        )

    # --------------------------------------------------
    # 2. Analitzar realment l'estructura del Python
    # --------------------------------------------------

    tree = ast.parse(text)

    analyze_function = None

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.AsyncFunctionDef)
            and node.name == "analyze_site"
        ):
            analyze_function = node
            break

    if analyze_function is None:
        raise RuntimeError(
            "No s'ha trobat la funció analyze_site."
        )

    calls_to_patch = []

    for node in ast.walk(analyze_function):
        if not isinstance(node, ast.Call):
            continue

        if not (
            isinstance(node.func, ast.Name)
            and node.func.id == "AnalyzeResponse"
        ):
            continue

        existing_keywords = {
            keyword.arg
            for keyword in node.keywords
            if keyword.arg is not None
        }

        missing_detected = (
            "detected_language"
            not in existing_keywords
        )

        missing_analysis = (
            "analysis_languages"
            not in existing_keywords
        )

        if not (
            missing_detected
            or missing_analysis
        ):
            continue

        status_value = get_status_value(node)

        calls_to_patch.append(
            (
                node,
                status_value,
                missing_detected,
                missing_analysis,
            )
        )

    # --------------------------------------------------
    # 3. Inserir els camps abans del ')' de cada call
    # --------------------------------------------------

    lines = text.splitlines(
        keepends=True
    )

    # De baix cap amunt perquè les insercions
    # no alterin els números de línia pendents.
    calls_to_patch.sort(
        key=lambda item: item[0].end_lineno or 0,
        reverse=True,
    )

    patched_count = 0

    for (
        call,
        status_value,
        missing_detected,
        missing_analysis,
    ) in calls_to_patch:
        if call.end_lineno is None:
            continue

        closing_index = (
            call.end_lineno - 1
        )

        closing_line = lines[
            closing_index
        ]

        indentation = (
            closing_line[
                : len(closing_line)
                - len(
                    closing_line.lstrip()
                )
            ]
        )

        field_indentation = (
            indentation + "    "
        )

        inserted_lines = []

        # L'early return de robots.txt succeeix
        # abans de poder detectar l'idioma HTML.
        if status_value == "robots_blocked":
            if missing_detected:
                inserted_lines.append(
                    field_indentation
                    + "detected_language=None,\n"
                )

            if missing_analysis:
                inserted_lines.append(
                    field_indentation
                    + "analysis_languages=languages,\n"
                )

        else:
            if missing_detected:
                inserted_lines.append(
                    field_indentation
                    + "detected_language=detected_language,\n"
                )

            if missing_analysis:
                inserted_lines.append(
                    field_indentation
                    + "analysis_languages=analysis_languages,\n"
                )

        if inserted_lines:
            lines[
                closing_index:
                closing_index
            ] = inserted_lines

            patched_count += 1

    repaired_text = "".join(lines)

    # --------------------------------------------------
    # 4. Verificació abans de desar
    # --------------------------------------------------

    ast.parse(repaired_text)

    if (
        "detected_language=detected_language,"
        not in repaired_text
    ):
        raise RuntimeError(
            "No s'ha pogut afegir "
            "detected_language al return final."
        )

    if (
        "analysis_languages=analysis_languages,"
        not in repaired_text
    ):
        raise RuntimeError(
            "No s'ha pogut afegir "
            "analysis_languages al return final."
        )

    MAIN_PATH.write_text(
        repaired_text,
        encoding="utf-8",
    )

    print(
        f"Pas 12D reparat correctament. "
        f"AnalyzeResponse modificats: {patched_count}"
    )


if __name__ == "__main__":
    main()