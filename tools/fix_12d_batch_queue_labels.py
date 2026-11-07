from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

APP_PATH = (
    ROOT
    / "apps"
    / "dashboard"
    / "src"
    / "App.tsx"
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
            f"{description}. Coincidències: {count}"
        )

    return text.replace(
        old,
        new,
        1,
    )


def main():
    text = APP_PATH.read_text(
        encoding="utf-8"
    )

    # ----------------------------------------------
    # 1. Estat amb les empreses pendents de la cua
    # ----------------------------------------------

    if (
        "batchQueuedOrganizationIds"
        not in text
    ):
        old = """  const [batchProgress, setBatchProgress] = useState({
    completed: 0,
    total: 0,
  })
"""

        new = """  const [batchProgress, setBatchProgress] = useState({
    completed: 0,
    total: 0,
  })

  const [
    batchQueuedOrganizationIds,
    setBatchQueuedOrganizationIds,
  ] = useState<string[]>([])
"""

        text = replace_once(
            text,
            old,
            new,
            "l'estat de la cua",
        )

    # ----------------------------------------------
    # 2. Buidar la cua en reiniciar la cerca
    # ----------------------------------------------

    old = """    setBatchProgress({
      completed: 0,
      total: 0,
    })
  }
"""

    new = """    setBatchProgress({
      completed: 0,
      total: 0,
    })

    setBatchQueuedOrganizationIds([])
  }
"""

    if (
        old in text
        and "setBatchQueuedOrganizationIds([])"
        not in text[
            text.find("const clearCurrentSearch"):
            text.find("const handleLocationQueryChange")
        ]
    ):
        text = replace_once(
            text,
            old,
            new,
            "el reinici de la cua",
        )

    # ----------------------------------------------
    # 3. Omplir la cua quan comença el lot
    # ----------------------------------------------

    old = """    setBatchProgress({
      completed: 0,
      total: candidates.length,
    })

    setNotice(
"""

    new = """    setBatchProgress({
      completed: 0,
      total: candidates.length,
    })

    setBatchQueuedOrganizationIds(
      candidates.map(
        (organization) => organization.id,
      ),
    )

    setNotice(
"""

    if old in text:
        text = replace_once(
            text,
            old,
            new,
            "l'inici de la cua",
        )
    elif (
        "setBatchQueuedOrganizationIds("
        not in text[
            text.find(
                "const analyzeVisibleWebsites"
            ):
            text.find(
                "let completed = 0"
            )
        ]
    ):
        raise RuntimeError(
            "No s'ha pogut localitzar "
            "l'inici de l'anàlisi per lots."
        )

    # ----------------------------------------------
    # 4. Treure una empresa de la cua quan acaba
    # ----------------------------------------------

    old = """          setAnalyzingOrganizationId((currentId) =>
            currentId === organization.id
              ? null
              : currentId,
          )
        }

        if (index < candidates.length - 1) {
"""

    new = """          setAnalyzingOrganizationId((currentId) =>
            currentId === organization.id
              ? null
              : currentId,
          )

          setBatchQueuedOrganizationIds(
            (currentIds) =>
              currentIds.filter(
                (organizationId) =>
                  organizationId !==
                  organization.id,
              ),
          )
        }

        if (index < candidates.length - 1) {
"""

    if old in text:
        text = replace_once(
            text,
            old,
            new,
            "la sortida d'una empresa de la cua",
        )
    elif (
        "currentIds.filter("
        not in text[
            text.find(
                "const analyzeVisibleWebsites"
            ):
            text.find(
                "const pause"
            )
            if text.find("const pause") > 0
            else len(text)
        ]
    ):
        raise RuntimeError(
            "No s'ha trobat el finally "
            "de l'anàlisi per lots."
        )

    # ----------------------------------------------
    # 5. Mostrar Analitzant... / En cua
    # ----------------------------------------------

    old = """                                    {analyzingOrganizationId ===
                                    organization.id
                                      ? 'Analitzant...'
                                      : siteAnalyses[organization.id]
                                        ? 'Torna a analitzar'
                                        : 'Analitza la web'}
"""

    new = """                                    {analyzingOrganizationId ===
                                    organization.id
                                      ? 'Analitzant...'
                                      : isBatchAnalyzing &&
                                          batchQueuedOrganizationIds.includes(
                                            organization.id,
                                          )
                                        ? 'En cua'
                                        : siteAnalyses[organization.id]
                                          ? 'Torna a analitzar'
                                          : 'Analitza la web'}
"""

    if old in text:
        text = replace_once(
            text,
            old,
            new,
            "el text del botó",
        )
    elif (
        "'En cua'"
        not in text
    ):
        raise RuntimeError(
            "No s'ha trobat el text "
            "del botó Analitza la web."
        )

    APP_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "12D-fix B2b aplicat: "
        "Analitzant... i En cua disponibles."
    )


if __name__ == "__main__":
    main()