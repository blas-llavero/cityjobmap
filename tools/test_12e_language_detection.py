from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(
        ROOT
        / "services"
        / "api"
    ),
)

from app.main import detect_text_language


TESTS = {
    "en": """
        <html><body>
        Our company is looking for talented people.
        Explore careers, jobs and employment opportunities.
        Contact our team and work with us.
        The company works with technology and software.
        Careers jobs employment team company contact.
        </body></html>
    """,

    "de": """
        <html><body>
        Unser Unternehmen sucht neue Mitarbeiter.
        Karriere, Stellen und Stellenangebote.
        Arbeiten Sie mit unserem Team.
        Kontakt und Bewerbung sind hier verfügbar.
        Karriere Stellen Bewerbung Unternehmen Mitarbeiter.
        </body></html>
    """,

    "fr": """
        <html><body>
        Notre entreprise recrute de nouveaux collaborateurs.
        Consultez nos emplois et notre espace recrutement.
        Contactez notre équipe pour les opportunités.
        Carrières emplois recrutement entreprise équipe.
        </body></html>
    """,

    "it": """
        <html><body>
        La nostra azienda cerca nuovi collaboratori.
        Consulta le opportunita di lavoro e carriera.
        Lavora con noi e invia la candidatura.
        Azienda lavoro carriera candidatura contatti squadra.
        </body></html>
    """,

    "ca": """
        <html><body>
        La nostra empresa busca professionals.
        Consulta les oportunitats de feina.
        Treballa amb nosaltres i envia la candidatura.
        Empresa equip feina contacte oportunitats treballa.
        </body></html>
    """,

    "es": """
        <html><body>
        Nuestra empresa busca profesionales.
        Consulta las oportunidades de empleo y vacantes.
        Trabaja con nosotros y envia tu candidatura.
        Empresa equipo empleo contacto oportunidades trabaja.
        </body></html>
    """,
}


failed = False

for expected, html in TESTS.items():
    detected = detect_text_language(
        html
    )

    ok = detected == expected

    print(
        f"{expected}: "
        f"detectat={detected} "
        f"{'OK' if ok else 'ERROR'}"
    )

    failed = failed or not ok


if failed:
    raise SystemExit(1)

print(
    "Test 12E-A completat correctament."
)