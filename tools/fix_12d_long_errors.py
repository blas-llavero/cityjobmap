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

    old = """.analysis-error {
  display: block;
  color: #b23434;
  font-size: 10px;
  line-height: 1.4;
}
"""

    new = """.analysis-error {
  display: -webkit-box;
  width: 100%;
  max-width: 240px;
  margin-top: 5px;
  overflow: hidden;
  overflow-wrap: anywhere;
  word-break: break-word;
  color: #b23434;
  font-size: 10px;
  line-height: 1.4;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
"""

    if old in css:
        css = css.replace(
            old,
            new,
            1,
        )
    elif (
        "-webkit-line-clamp: 2;"
        in css
        and ".analysis-error"
        in css
    ):
        print(
            "El fix dels errors llargs "
            "ja estava aplicat."
        )
    else:
        raise RuntimeError(
            "No s'ha trobat el bloc "
            ".analysis-error esperat."
        )

    marker = (
        "/* 12D-fix: estabilitat horitzontal */"
    )

    if marker not in css:
        css += """

/* 12D-fix: estabilitat horitzontal */

.opportunity-card {
  min-width: 0;
  max-width: 260px;
  overflow: hidden;
  overflow-wrap: anywhere;
}

.opportunity-card p,
.opportunity-evidence,
.opportunity-card a,
.site-analysis-links a {
  overflow-wrap: anywhere;
  word-break: break-word;
}

.opportunity-actions {
  min-width: 0;
  max-width: 100%;
}

"""

    CSS_PATH.write_text(
        css,
        encoding="utf-8",
    )

    print(
        "12D-fix B1 aplicat: "
        "errors i URLs llargues limitats."
    )


if __name__ == "__main__":
    main()