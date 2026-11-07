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
        "/* 12D-fix B2a: taula responsive "
        "sense amplades minimes rigides */"
    )

    if marker in css:
        print(
            "El 12D-fix B2a ja estava aplicat."
        )
        return

    css += r"""

/* 12D-fix B2a: taula responsive sense amplades minimes rigides */

.table-wrapper {
  width: 100%;
  max-width: 100%;
}

.table-wrapper table {
  width: 100%;
  max-width: 100%;
  table-layout: fixed;
}

.table-wrapper th,
.table-wrapper td {
  min-width: 0;
  overflow-wrap: anywhere;
  word-break: break-word;
}

/* Empresa */
.table-wrapper th:nth-child(1),
.table-wrapper td:nth-child(1) {
  width: 19%;
}

/* Municipi */
.table-wrapper th:nth-child(2),
.table-wrapper td:nth-child(2) {
  width: 10%;
}

/* Distància */
.table-wrapper th:nth-child(3),
.table-wrapper td:nth-child(3) {
  width: 9%;
}

/* Perfils */
.table-wrapper th:nth-child(4),
.table-wrapper td:nth-child(4) {
  width: 21%;
}

/* Puntuació */
.table-wrapper th:nth-child(5),
.table-wrapper td:nth-child(5) {
  width: 9%;
}

/* Estat */
.table-wrapper th:nth-child(6),
.table-wrapper td:nth-child(6) {
  width: 11%;
}

/* Accions */
.table-wrapper th:nth-child(7),
.table-wrapper td:nth-child(7) {
  width: 21%;
}

.result-name,
.profile-matches,
.row-actions {
  min-width: 0;
  max-width: 100%;
}

.row-action-buttons {
  min-width: 0;
  max-width: 100%;
}

.row-action-buttons button,
.row-action-buttons a {
  max-width: 100%;
  white-space: normal;
}

.analysis-error {
  max-width: 100%;
}
"""

    CSS_PATH.write_text(
        css,
        encoding="utf-8",
    )

    print(
        "12D-fix B2a aplicat: "
        "taula flexible i amplades minimes eliminades."
    )


if __name__ == "__main__":
    main()