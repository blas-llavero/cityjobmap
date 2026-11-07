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

    # Anàlisi individual
    old_individual = '''      const analysis = await analyzeWebsite(organization.website)
'''

    new_individual = '''      const analysis = await analyzeWebsite(
        organization.website,
        selectedLanguageCodes,
      )
'''

    if old_individual in text:
        text = text.replace(
            old_individual,
            new_individual,
            1,
        )

    # Anàlisi per lots
    old_batch = '''          const analysis = await analyzeWebsite(
            organization.website,
            controller.signal,
          )
'''

    new_batch = '''          const analysis = await analyzeWebsite(
            organization.website,
            selectedLanguageCodes,
            controller.signal,
          )
'''

    if old_batch in text:
        text = text.replace(
            old_batch,
            new_batch,
            1,
        )

    # Protecció si no hi ha idioma
    marker = '''  const analyzeOrganizationWebsite = async (
    organization: OrganizationResult,
  ) => {
'''

    if (
        marker in text
        and "Selecciona com a mínim un idioma de cerca" not in text
    ):
        replacement = '''  const analyzeOrganizationWebsite = async (
    organization: OrganizationResult,
  ) => {
    if (selectedLanguageCodes.length === 0) {
      setNotice(
        'Selecciona com a mínim un idioma de cerca abans d’analitzar la web.',
      )
      return
    }

'''

        text = text.replace(
            marker,
            replacement,
            1,
        )

    # Protecció del lot
    batch_marker = '''  const analyzeVisibleWebsites = async () => {
    if (isBatchAnalyzing) {
      return
    }
'''

    batch_replacement = '''  const analyzeVisibleWebsites = async () => {
    if (isBatchAnalyzing) {
      return
    }

    if (selectedLanguageCodes.length === 0) {
      setNotice(
        'Selecciona com a mínim un idioma de cerca abans d’analitzar les webs.',
      )
      return
    }
'''

    if batch_marker in text:
        text = text.replace(
            batch_marker,
            batch_replacement,
            1,
        )

    APP_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "Idiomes connectats amb l'anàlisi de les webs."
    )


if __name__ == "__main__":
    main()