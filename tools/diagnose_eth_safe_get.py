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

from app.main import (
    safe_get,
    load_robots,
)


async def main():
    url = "https://ethz.ch"

    timeout = httpx.Timeout(
        20.0
    )

    async with httpx.AsyncClient(
        timeout=timeout
    ) as client:

        print("=== LOAD_ROBOTS ===")

        try:
            robots, delay = await load_robots(
                client,
                url,
            )

            print(
                "robots.txt: OK"
            )

            print(
                "crawl delay:",
                delay,
            )

            print(
                "can_fetch home:",
                robots.can_fetch(
                    "*",
                    url,
                ),
            )

        except Exception as exc:
            print(
                "ERROR LOAD_ROBOTS:",
                type(exc).__name__,
                repr(exc),
            )

        print()
        print("=== SAFE_GET ===")

        try:
            response, final_url = await safe_get(
                client,
                url,
            )

            print(
                "safe_get: OK"
            )

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
                "ERROR SAFE_GET:",
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