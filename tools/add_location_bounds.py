from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = ROOT / "services" / "api" / "app" / "main.py"


def replace_once(text, old, new, description):
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"No s'ha pogut aplicar {description}. "
            f"Coincidències: {count}"
        )

    return text.replace(old, new, 1)


def main():
    text = MAIN_PATH.read_text(encoding="utf-8")

    old_model = '''class GeocodeResponse(BaseModel):
    query: str
    display_name: str
    latitude: float
    longitude: float
    country_code: str
    location_name: str
'''

    new_model = '''class GeocodeResponse(BaseModel):
    query: str
    display_name: str
    latitude: float
    longitude: float
    country_code: str
    location_name: str
    bounding_box: list[float] | None = None
'''

    if old_model in text:
        text = replace_once(
            text,
            old_model,
            new_model,
            "el model GeocodeResponse",
        )

    old_return = '''    return GeocodeResponse(
        query=query,
        display_name=str(
            result.get("display_name", query)
        ),
        latitude=latitude,
        longitude=longitude,
        country_code=country_code,
        location_name=str(location_name),
    )
'''

    new_return = '''    raw_bounding_box = result.get("boundingbox")

    bounding_box = None

    if (
        isinstance(raw_bounding_box, list)
        and len(raw_bounding_box) == 4
    ):
        try:
            bounding_box = [
                float(raw_bounding_box[0]),
                float(raw_bounding_box[1]),
                float(raw_bounding_box[2]),
                float(raw_bounding_box[3]),
            ]
        except (TypeError, ValueError):
            bounding_box = None

    return GeocodeResponse(
        query=query,
        display_name=str(
            result.get("display_name", query)
        ),
        latitude=latitude,
        longitude=longitude,
        country_code=country_code,
        location_name=str(location_name),
        bounding_box=bounding_box,
    )
'''

    if old_return in text:
        text = replace_once(
            text,
            old_return,
            new_return,
            "el retorn de la geocodificació",
        )

    MAIN_PATH.write_text(text, encoding="utf-8")

    print("Bounding box afegit correctament.")


if __name__ == "__main__":
    main()