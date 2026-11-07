from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PATH = (
    ROOT
    / "apps"
    / "dashboard"
    / "src"
    / "services"
    / "siteAnalysisApi.ts"
)


def main():
    text = PATH.read_text(
        encoding="utf-8"
    )

    old = '''  blocked_urls: string[]
}
'''

    new = '''  blocked_urls: string[]
  detected_language?: string | null
  analysis_languages?: string[]
}
'''

    if old in text:
        text = text.replace(
            old,
            new,
            1,
        )
    elif "detected_language?" not in text:
        raise RuntimeError(
            "No s'ha trobat SiteAnalysis."
        )

    PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "siteAnalysisApi.ts actualitzat."
    )


if __name__ == "__main__":
    main()