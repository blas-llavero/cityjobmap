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

    old_call = '''        evaluation: evaluateOrganization(
          organization,
          selectedProfessionIds,
        ),
'''

    new_call = '''        evaluation: evaluateOrganization(
          organization,
          selectedProfessionIds,
          selectedLanguageCodes,
        ),
'''

    if old_call not in text:
        if (
            "selectedLanguageCodes," in text
            and "evaluateOrganization(" in text
        ):
            print(
                "Els idiomes ja estaven connectats "
                "amb el classificador."
            )
            return

        raise RuntimeError(
            "No s'ha trobat la crida "
            "a evaluateOrganization."
        )

    text = text.replace(
        old_call,
        new_call,
        1,
    )

    old_dependencies = '''  }, [organizations, selectedProfessionIds])
'''

    new_dependencies = '''  }, [
    organizations,
    selectedProfessionIds,
    selectedLanguageCodes,
  ])
'''

    if old_dependencies in text:
        text = text.replace(
            old_dependencies,
            new_dependencies,
            1,
        )

    APP_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "Idiomes connectats amb "
        "la classificació professional."
    )


if __name__ == "__main__":
    main()