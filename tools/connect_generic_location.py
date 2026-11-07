from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = (
    ROOT
    / "apps"
    / "dashboard"
    / "src"
    / "App.tsx"
)


def replace_once(
    text,
    old,
    new,
    description,
):
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"No s'ha pogut aplicar "
            f"«{description}». "
            f"Coincidències: {count}"
        )

    return text.replace(
        old,
        new,
        1,
    )


def main():
    app = APP_PATH.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------
    # 1. Crida genèrica a Overpass
    # --------------------------------------------

    old_call = '''      const foundOrganizations = await searchOrganizations(
        targetRadiusKm,
        controller.signal,
      )
'''

    new_call = '''      if (!resolvedLocation) {
        throw new Error(
          'No hi ha cap ubicació seleccionada.',
        )
      }

      const foundOrganizations =
        await searchOrganizations(
          resolvedLocation,
          targetRadiusKm,
          controller.signal,
        )
'''

    if old_call in app:
        app = replace_once(
            app,
            old_call,
            new_call,
            "la crida a Overpass",
        )

    # --------------------------------------------
    # 2. Missatges dinàmics
    # --------------------------------------------

    old_notice = '''    setNotice(
      targetRadiusKm === 0
        ? 'Cercant i classificant organitzacions de Reus...'
        : `Cercant i classificant organitzacions fins a ${targetRadiusKm} km de Reus...`,
    )
'''

    new_notice = '''    const searchLocationName =
      resolvedLocation?.location_name ??
      'la ubicació seleccionada'

    setNotice(
      targetRadiusKm === 0
        ? `Cercant i classificant organitzacions a ${searchLocationName}...`
        : `Cercant i classificant organitzacions fins a ${targetRadiusKm} km de ${searchLocationName}...`,
    )
'''

    if old_notice in app:
        app = replace_once(
            app,
            old_notice,
            new_notice,
            "els missatges d'inici",
        )

    old_completed = '''      setNotice(
        targetRadiusKm === 0
          ? `Cerca completada a Reus: ${foundOrganizations.length} organitzacions analitzades.`
          : `Cerca completada fins a ${targetRadiusKm} km: ${foundOrganizations.length} organitzacions analitzades dins del radi.`,
      )
'''

    new_completed = '''      setNotice(
        targetRadiusKm === 0
          ? `Cerca completada a ${searchLocationName}: ${foundOrganizations.length} organitzacions analitzades.`
          : `Cerca completada fins a ${targetRadiusKm} km de ${searchLocationName}: ${foundOrganizations.length} organitzacions analitzades dins del radi.`,
      )
'''

    if old_completed in app:
        app = replace_once(
            app,
            old_completed,
            new_completed,
            "el missatge de finalització",
        )

    # --------------------------------------------
    # 3. Eliminar protecció temporal del Pas 11B
    # --------------------------------------------

    temporary_guard = '''    if (
      resolvedLocation.location_name
        .toLocaleLowerCase('ca') !== 'reus'
    ) {
      setNotice(
        'Ubicació validada correctament. Encara no hem connectat aquesta ubicació a Overpass; ho farem al pas 11C.',
      )
      return
    }

'''

    if temporary_guard in app:
        app = app.replace(
            temporary_guard,
            "",
            1,
        )

    # --------------------------------------------
    # 4. Eliminar locationReadyForCurrentSearch
    # --------------------------------------------

    old_area = '''  const selectedLocationName =
    resolvedLocation?.location_name ?? 'Ubicació pendent'

  const locationReadyForCurrentSearch =
    resolvedLocation?.location_name
      .toLocaleLowerCase('ca') === 'reus'

  const currentArea =
'''

    new_area = '''  const selectedLocationName =
    resolvedLocation?.location_name ?? 'Ubicació pendent'

  const currentArea =
'''

    if old_area in app:
        app = replace_once(
            app,
            old_area,
            new_area,
            "locationReadyForCurrentSearch",
        )

    # --------------------------------------------
    # 5. Eliminar avís temporal del Pas 11B
    # --------------------------------------------

    transition_note = '''          {resolvedLocation &&
            !locationReadyForCurrentSearch && (
              <div className="location-transition-note">
                Ubicació validada. Al pas 11C la
                connectarem amb la cerca d’empreses.
              </div>
            )}
'''

    if transition_note in app:
        app = app.replace(
            transition_note,
            "",
            1,
        )

    # --------------------------------------------
    # 6. Botó principal genèric
    # --------------------------------------------

    old_button = '''            disabled={
              selectedProfessionIds.length === 0 ||
              isSearching ||
              isLocating ||
              !resolvedLocation ||
              !locationReadyForCurrentSearch
            }
          >
            {isSearching
              ? 'Cercant organitzacions...'
              : !resolvedLocation
                ? 'Localitza una ubicació'
                : locationReadyForCurrentSearch
                  ? `Preparar cerca a ${resolvedLocation.location_name}`
                  : 'Ubicació preparada · falta el pas 11C'}
          </button>
'''

    new_button = '''            disabled={
              selectedProfessionIds.length === 0 ||
              isSearching ||
              isLocating ||
              !resolvedLocation
            }
          >
            {isSearching
              ? 'Cercant organitzacions...'
              : !resolvedLocation
                ? 'Localitza una ubicació'
                : `Preparar cerca a ${resolvedLocation.location_name}`}
          </button>
'''

    if old_button in app:
        app = replace_once(
            app,
            old_button,
            new_button,
            "el botó principal",
        )

    # --------------------------------------------
    # 7. Municipi de la taula
    # --------------------------------------------

    old_municipality = '''                            {organization.municipality ===
                            'Municipi no indicat'
                              ? radiusKm === 0
                                ? 'Reus'
                                : 'No indicat'
                              : organization.municipality}
'''

    new_municipality = '''                            {organization.municipality ||
                              selectedLocationName}
'''

    if old_municipality in app:
        app = replace_once(
            app,
            old_municipality,
            new_municipality,
            "el municipi dels resultats",
        )

    # --------------------------------------------
    # 8. Text de l'estadística de radi
    # --------------------------------------------

    old_radius_small = """              <small>{radiusKm === 0 ? 'Només Reus' : currentArea}</small>
"""

    new_radius_small = """              <small>
                {radiusKm === 0
                  ? `Àrea inicial de ${selectedLocationName}`
                  : currentArea}
              </small>
"""

    if old_radius_small in app:
        app = replace_once(
            app,
            old_radius_small,
            new_radius_small,
            "el text del radi",
        )

    APP_PATH.write_text(
        app,
        encoding="utf-8",
    )

    print(
        "Dashboard connectat amb la ubicació seleccionada."
    )


if __name__ == "__main__":
    main()