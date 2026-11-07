from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

APP_PATH = (
    ROOT
    / "apps"
    / "dashboard"
    / "src"
    / "App.tsx"
)

CSS_PATH = (
    ROOT
    / "apps"
    / "dashboard"
    / "src"
    / "App.css"
)


def print_section(
    title: str,
    lines: list[str],
    start: int,
    end: int,
) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)

    start = max(0, start)
    end = min(len(lines), end)

    for index in range(start, end):
        print(
            f"{index + 1:04d}: "
            f"{lines[index]}"
        )


def find_contexts(
    title: str,
    lines: list[str],
    patterns: list[str],
    before: int = 12,
    after: int = 24,
) -> None:
    found = []

    for index, line in enumerate(lines):
        lowered = line.lower()

        if any(
            pattern.lower() in lowered
            for pattern in patterns
        ):
            found.append(index)

    if not found:
        print()
        print(
            f"[NO TROBAT] {title}: "
            f"{patterns}"
        )
        return

    # Agrupar coincidències properes
    groups = []

    for index in found:
        if (
            groups
            and index <= groups[-1][-1] + 20
        ):
            groups[-1].append(index)
        else:
            groups.append([index])

    for number, group in enumerate(
        groups[:8],
        start=1,
    ):
        print_section(
            f"{title} — bloc {number}",
            lines,
            group[0] - before,
            group[-1] + after + 1,
        )


def main() -> None:
    app_text = APP_PATH.read_text(
        encoding="utf-8"
    )

    css_text = CSS_PATH.read_text(
        encoding="utf-8"
    )

    app_lines = app_text.splitlines()
    css_lines = css_text.splitlines()

    print(
        "DIAGNÒSTIC 12D-FIX — "
        "CityJobMap"
    )

    print()
    print(
        f"App.tsx: {len(app_lines)} línies"
    )

    print(
        f"App.css: {len(css_lines)} línies"
    )

    find_contexts(
        "ESTATS I VARIABLES DEL LOT",
        app_lines,
        [
            "batch",
            "pause",
            "paused",
            "stop",
            "stopped",
            "analitza webs visibles",
        ],
    )

    find_contexts(
        "ORDENACIÓ DELS RESULTATS",
        app_lines,
        [
            ".sort(",
            "sort(",
            "statuspriority",
            "status priority",
            "visibleorganizations",
            "sorted",
            "ordered",
        ],
    )

    find_contexts(
        "ANÀLISI INDIVIDUAL I ESTAT ANALITZANT",
        app_lines,
        [
            "analyzing",
            "analysing",
            "analitzant",
            "analyzesite",
            "analyzewebsite",
        ],
    )

    find_contexts(
        "ERRORS DE WEB",
        app_lines,
        [
            "error",
            "failed to fetch",
            "403",
            "siteanalysis",
        ],
    )

    find_contexts(
        "RENDER DE LES FILES / TAULA",
        app_lines,
        [
            "<table",
            "<tr",
            "organization-row",
            "organizations.map",
            ".map((organization",
        ],
    )

    find_contexts(
        "CSS DE TAULA I OVERFLOW",
        css_lines,
        [
            "overflow",
            "table",
            "actions",
            "opportunity",
            "error",
        ],
        before=8,
        after=16,
    )


if __name__ == "__main__":
    main()