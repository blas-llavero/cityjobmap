from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CSS_PATH = (
    ROOT
    / "apps"
    / "dashboard"
    / "src"
    / "App.css"
)


def main():
    css = CSS_PATH.read_text(
        encoding="utf-8"
    )

    marker = (
        "/* 12D-fix B2c: capcalera puntuacio */"
    )

    if marker in css:
        print(
            "El 12D-fix B2c ja estava aplicat."
        )
        return

    css += r"""

/* 12D-fix B2c: capcalera puntuacio */

/* Perfils: 21% -> 20% */
.table-wrapper th:nth-child(4),
.table-wrapper td:nth-child(4) {
  width: 20%;
}

/* Puntuacio: 9% -> 10% */
.table-wrapper th:nth-child(5),
.table-wrapper td:nth-child(5) {
  width: 10%;
}

.table-wrapper th:nth-child(5) {
  white-space: nowrap;
}
"""

    CSS_PATH.write_text(
        css,
        encoding="utf-8",
    )

    print(
        "12D-fix B2c aplicat: "
        "Puntuacio ja no s'hauria de partir."
    )


if __name__ == "__main__":
    main()