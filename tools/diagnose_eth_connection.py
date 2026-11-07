import socket
import httpx


host = "ethz.ch"

print("=== DNS ===")

try:
    addresses = socket.getaddrinfo(
        host,
        443,
        type=socket.SOCK_STREAM,
    )

    unique = []

    for item in addresses:
        address = item[4][0]

        if address not in unique:
            unique.append(address)

    for address in unique:
        print(address)

except Exception as exc:
    print(
        "ERROR DNS:",
        type(exc).__name__,
        str(exc),
    )


print()
print("=== HTTPX ===")

try:
    with httpx.Client(
        timeout=20.0,
        follow_redirects=True,
        headers={
            "User-Agent": (
                "CityJobMap/0.1 "
                "(local open-source job research tool)"
            )
        },
    ) as client:
        response = client.get(
            "https://ethz.ch"
        )

        print(
            "Status:",
            response.status_code,
        )

        print(
            "URL final:",
            response.url,
        )

        print(
            "Bytes:",
            len(response.content),
        )

except Exception as exc:
    print(
        "ERROR HTTPX:",
        type(exc).__name__,
        str(exc),
    )