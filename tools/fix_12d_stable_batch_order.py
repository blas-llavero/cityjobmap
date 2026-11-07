from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

APP_PATH = (
    ROOT
    / "apps"
    / "dashboard"
    / "src"
    / "App.tsx"
)


def main():
    text = APP_PATH.read_text(
        encoding="utf-8"
    )

    old_start = """    return [...baseOrganizations].sort((first, second) => {
      const firstAnalysis =
        siteAnalyses[first.organization.id]
"""

    new_start = """    /*
     * Durant una anàlisi per lots mantenim exactament
     * l'ordre que ja tenien els resultats.
     *
     * Això evita que les files saltin de posició cada
     * vegada que acaba l'anàlisi d'una empresa.
     */
    if (isBatchAnalyzing) {
      return [...baseOrganizations]
    }

    return [...baseOrganizations].sort((first, second) => {
      const firstAnalysis =
        siteAnalyses[first.organization.id]
"""

    if old_start not in text:
        if (
            "if (isBatchAnalyzing) {" in text
            and "return [...baseOrganizations]" in text
        ):
            print(
                "L'estabilització del lot "
                "ja estava aplicada."
            )
        else:
            raise RuntimeError(
                "No s'ha trobat el bloc "
                "visibleOrganizations esperat."
            )
    else:
        text = text.replace(
            old_start,
            new_start,
            1,
        )

    old_dependencies = """    showLowRelevance,
    siteAnalyses,
  ])
"""

    new_dependencies = """    showLowRelevance,
    siteAnalyses,
    isBatchAnalyzing,
  ])
"""

    if old_dependencies in text:
        text = text.replace(
            old_dependencies,
            new_dependencies,
            1,
        )
    elif "isBatchAnalyzing," not in text[
        text.find("const visibleOrganizations"):
        text.find(
            "const unanalyzedVisibleWebsiteCount"
        )
    ]:
        raise RuntimeError(
            "No s'ha pogut afegir "
            "isBatchAnalyzing a les dependències."
        )

    APP_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "12D-fix A aplicat: "
        "la llista queda estable durant el lot."
    )


if __name__ == "__main__":
    main()