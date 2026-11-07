from pathlib import Path
import sys
import asyncio


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(
        ROOT
        / "services"
        / "api"
    ),
)

from app.main import (
    AnalyzeRequest,
    analyze_site,
)


async def main():
    request = AnalyzeRequest(
        website="https://ethz.ch",
        languages=["en"],
    )

    print(
        "=== ANALYZE_SITE DIRECTE ==="
    )

    try:
        result = await analyze_site(
            request
        )

        print("ANALYZE_SITE: OK")
        print(
            "status:",
            result.status,
        )
        print(
            "status_label:",
            result.status_label,
        )
        print(
            "detected_language:",
            result.detected_language,
        )
        print(
            "analysis_languages:",
            result.analysis_languages,
        )
        print(
            "career_url:",
            result.career_url,
        )
        print(
            "contact_url:",
            result.contact_url,
        )

        print()
        print("PAGES_CHECKED:")

        for url in result.pages_checked:
            print(
                " -",
                url,
            )

        print()
        print("BLOCKED_URLS:")

        for url in result.blocked_urls:
            print(
                " -",
                url,
            )

    except Exception as exc:
        print(
            "ANALYZE_SITE ERROR:"
        )
        print(
            "tipus:",
            type(exc).__name__,
        )
        print(
            "repr:",
            repr(exc),
        )

        detail = getattr(
            exc,
            "detail",
            None,
        )

        if detail is not None:
            print(
                "detail:",
                detail,
            )


asyncio.run(main())