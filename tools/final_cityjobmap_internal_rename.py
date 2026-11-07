from pathlib import Path
import shutil

root = Path.cwd()

old_api_dir = root / "services" / "scout-api"
new_api_dir = root / "services" / "api"

old_frontend_api = (
    root
    / "apps"
    / "dashboard"
    / "src"
    / "services"
    / "siteAnalysisApi.ts"
)

new_frontend_api = (
    root
    / "apps"
    / "dashboard"
    / "src"
    / "services"
    / "siteAnalysisApi.ts"
)

# --------------------------------------------------
# 1. Còpies de seguretat dels fitxers importants
# --------------------------------------------------

important_files = [
    root / "package.json",
    root / "apps" / "dashboard" / "src" / "App.tsx",
    old_frontend_api,
    old_api_dir / "app" / "main.py",
]

for path in important_files:
    if not path.exists():
        continue

    backup = path.with_name(
        path.name + ".bak-before-final-cityjobmap-rename"
    )

    if not backup.exists():
        shutil.copy2(path, backup)


# --------------------------------------------------
# 2. Renombrar l'API del frontend
# --------------------------------------------------

if old_frontend_api.exists():
    if new_frontend_api.exists():
        raise RuntimeError(
            "Ja existeix siteAnalysisApi.ts."
        )

    old_frontend_api.rename(
        new_frontend_api
    )


# --------------------------------------------------
# 3. Renombrar services/api -> services/api
# --------------------------------------------------

if old_api_dir.exists():
    if new_api_dir.exists():
        raise RuntimeError(
            "Ja existeix services/api."
        )

    old_api_dir.rename(
        new_api_dir
    )


# --------------------------------------------------
# 4. Substitucions textuals
# --------------------------------------------------

replacements = [
    (
        "./services/siteAnalysisApi",
        "./services/siteAnalysisApi",
    ),
    (
        "services/api",
        "services/api",
    ),
    (
        r"services\api",
        r"services\api",
    ),
    (
        "CityJobMap",
        "CityJobMap",
    ),
    (
        "CityJobMap",
        "CityJobMap",
    ),
    (
        "cityjobmap",
        "cityjobmap",
    ),
]

allowed_extensions = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".py",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".toml",
    ".ps1",
    ".css",
    ".html",
}

excluded_directories = {
    "node_modules",
    ".venv",
    "dist",
    ".git",
    "__pycache__",
}

changed_files = []

for path in root.rglob("*"):
    if not path.is_file():
        continue

    if any(
        part in excluded_directories
        for part in path.parts
    ):
        continue

    if ".bak" in path.name:
        continue

    if path.suffix.lower() not in allowed_extensions:
        continue

    try:
        original = path.read_text(
            encoding="utf-8"
        )
    except UnicodeDecodeError:
        continue

    updated = original

    for old, new in replacements:
        updated = updated.replace(
            old,
            new,
        )

    if updated != original:
        path.write_text(
            updated,
            encoding="utf-8",
        )

        changed_files.append(
            path.relative_to(root)
        )


print()
print("Renombrat intern completat.")
print()

print("API backend:")
print(new_api_dir)

print()
print("API frontend:")
print(new_frontend_api)

print()
print("Fitxers actualitzats:")

for path in changed_files:
    print(" -", path)

print()