from pathlib import Path
import re
import shutil

ROOT = Path.cwd()

app_path = ROOT / "apps" / "dashboard" / "src" / "App.tsx"
api_path = ROOT / "services" / "scout-api" / "app" / "main.py"

# --------------------------------------------------
# Còpies de seguretat
# --------------------------------------------------

app_backup = app_path.with_name(
    "App.tsx.bak-before-cityjobmap"
)

api_backup = api_path.with_name(
    "main.py.bak-before-cityjobmap"
)

if not app_backup.exists():
    shutil.copy2(app_path, app_backup)

if not api_backup.exists():
    shutil.copy2(api_path, api_backup)

# --------------------------------------------------
# Frontend
# --------------------------------------------------

app = app_path.read_text(encoding="utf-8")

# Nom del projecte
app = app.replace(
    "CityJobMap",
    "CityJobMap",
)

# La ubicació inicial queda buida
app = app.replace(
    "useState('Reus, Spain')",
    "useState('')",
)

# Eliminar la ubicació resolta de Reus per defecte
pattern = re.compile(
    r"useState<GeocodedLocation \| null>\(\{"
    r".*?"
    r"\}\)",
    re.DOTALL,
)

app, replacements = pattern.subn(
    "useState<GeocodedLocation | null>(null)",
    app,
    count=1,
)

if replacements != 1:
    print(
        "AVÍS: no s'ha pogut substituir "
        "automàticament resolvedLocation."
    )

app_path.write_text(
    app,
    encoding="utf-8",
)

# --------------------------------------------------
# Backend
# --------------------------------------------------

api = api_path.read_text(encoding="utf-8")

api = api.replace(
    'APP_NAME = "CityJobMap API"',
    'APP_NAME = "CityJobMap API"',
)

api = api.replace(
    '"CityJobMap/0.1 "',
    '"CityJobMap/0.1 "',
)

api_path.write_text(
    api,
    encoding="utf-8",
)

print()
print("Canvis aplicats correctament.")
print()
print("Nom nou: CityJobMap")
print("Ubicació inicial: cap")
print()
print("Còpies de seguretat:")
print(app_backup)
print(api_backup)