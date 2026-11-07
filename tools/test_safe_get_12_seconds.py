from pathlib import Path
import sys
import asyncio
import httpx


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(
        ROOT
        / "services"
        / "api"
    ),
)

from app.main import safe_get


async def main():
    timeout = httpx.Timeout(
        12.0
    )

    async with httpx.AsyncClient(
        timeout=timeout
    ) as client:
        try:
            response, final_url = await safe_get(
                client,
                "https://ethz.ch",
            )

            print("SAFE_GET 12s: OK")
            print(
                "status:",
                response.status_code,
            )
            print(
                "url final:",
                final_url,
            )
            print(
                "bytes:",
                len(response.content),
            )

        except Exception as exc:
            print(
                "SAFE_GET 12s ERROR:",
                type(exc).__name__,
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