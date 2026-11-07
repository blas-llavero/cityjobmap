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

    old_signature = '''export async function analyzeWebsite(
  website: string,
  signal?: AbortSignal,
): Promise<SiteAnalysis> {
'''

    new_signature = '''export async function analyzeWebsite(
  website: string,
  languages: string[],
  signal?: AbortSignal,
): Promise<SiteAnalysis> {
'''

    if old_signature in text:
        text = text.replace(
            old_signature,
            new_signature,
            1,
        )

    old_body = '''    body: JSON.stringify({
      website,
    }),
'''

    new_body = '''    body: JSON.stringify({
      website,
      languages,
    }),
'''

    if old_body not in text:
        raise RuntimeError(
            "No s'ha trobat el body d'analyzeWebsite."
        )

    text = text.replace(
        old_body,
        new_body,
        1,
    )

    PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "siteAnalysisApi.ts preparat per enviar idiomes."
    )


if __name__ == "__main__":
    main()