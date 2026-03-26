#!/usr/bin/env python3
"""
Sprint 1 - Scanner básico de negocios con Google Places API (New).

- Hace Text Search por ubicación (lat/lng + radio)
- Usa Field Mask para pedir solo los campos necesarios
- Maneja paginación (nextPageToken) hasta ~60 resultados por query
- Imprime resultados en consola de forma legible
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Busca negocios con Google Places API (New) usando Text Search.",
    )
    parser.add_argument("--query", required=True, help="Categoría o término, ej: restaurant, cafe, plumber")
    parser.add_argument("--lat", required=True, type=float, help="Latitud del centro de búsqueda")
    parser.add_argument("--lng", required=True, type=float, help="Longitud del centro de búsqueda")
    parser.add_argument("--radius", type=float, default=1500, help="Radio en metros (default: 1500)")
    parser.add_argument("--max-results", type=int, default=60, help="Máximo de resultados a recuperar (default: 60)")
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key de Google Maps. Si no se especifica, usa GOOGLE_MAPS_API_KEY del entorno.",
    )
    parser.add_argument(
        "--page-delay",
        type=float,
        default=2.0,
        help="Espera entre páginas para nextPageToken (default: 2.0 segundos)",
    )
    return parser


def get_api_key(cli_value: Optional[str]) -> str:
    load_dotenv()
    api_key = cli_value or os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError(
            "No se encontró API key. Usa --api-key o define GOOGLE_MAPS_API_KEY en .env / variables de entorno.",
        )
    return api_key


def map_place_to_output(place: Dict[str, Any]) -> Dict[str, Any]:
    display_name = place.get("displayName", {}).get("text")
    location = place.get("location", {})

    return {
        "name": display_name,
        "formatted_address": place.get("formattedAddress"),
        # En Places API (New), el ID utilizable equivale al place_id clásico.
        "place_id": place.get("id"),
        "rating": place.get("rating"),
        # userRatingCount en New API = user_ratings_total en API legacy.
        "user_ratings_total": place.get("userRatingCount"),
        "website": place.get("websiteUri"),
        "formatted_phone_number": place.get("nationalPhoneNumber"),
        "url": place.get("googleMapsUri"),
        "geometry": {
            "location": {
                "lat": location.get("latitude"),
                "lng": location.get("longitude"),
            },
        },
        "business_status": place.get("businessStatus"),
    }


def search_places_text(
    api_key: str,
    query: str,
    lat: float,
    lng: float,
    radius: float,
    max_results: int,
    page_delay: float,
) -> List[Dict[str, Any]]:
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": ",".join(
            [
                "places.displayName",
                "places.formattedAddress",
                "places.id",
                "places.rating",
                "places.userRatingCount",
                "places.websiteUri",
                "places.nationalPhoneNumber",
                "places.googleMapsUri",
                "places.location",
                "places.businessStatus",
                "nextPageToken",
            ]
        ),
    }

    all_places: List[Dict[str, Any]] = []
    next_page_token: Optional[str] = None
    page_number = 1

    while len(all_places) < max_results:
        body: Dict[str, Any] = {
            "textQuery": query,
            "maxResultCount": min(20, max_results - len(all_places)),
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": radius,
                }
            },
        }

        if next_page_token:
            body["pageToken"] = next_page_token

        response = requests.post(PLACES_TEXT_SEARCH_URL, headers=headers, json=body, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(
                f"Error en Places API ({response.status_code}): {response.text}"
            )

        data = response.json()
        page_places = data.get("places", [])
        all_places.extend(page_places)

        print(f"Página {page_number}: recibidos {len(page_places)} lugares (acumulado={len(all_places)})")

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

        page_number += 1
        time.sleep(page_delay)

    return [map_place_to_output(p) for p in all_places[:max_results]]


def print_places(places: List[Dict[str, Any]]) -> None:
    if not places:
        print("No se encontraron resultados.")
        return

    print("\n" + "=" * 110)
    print(f"Total resultados: {len(places)}")
    print("=" * 110)

    for i, place in enumerate(places, start=1):
        geo = place.get("geometry", {}).get("location", {})
        print(f"\n[{i}] {place.get('name')}")
        print(f"    Dirección: {place.get('formatted_address')}")
        print(f"    Place ID: {place.get('place_id')}")
        print(f"    Rating: {place.get('rating')} | Reseñas: {place.get('user_ratings_total')}")
        print(f"    Estado negocio: {place.get('business_status')}")
        print(f"    Teléfono: {place.get('formatted_phone_number')}")
        print(f"    Website: {place.get('website')}")
        print(f"    Maps URL: {place.get('url')}")
        print(f"    Lat/Lng: {geo.get('lat')}, {geo.get('lng')}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        api_key = get_api_key(args.api_key)
        places = search_places_text(
            api_key=api_key,
            query=args.query,
            lat=args.lat,
            lng=args.lng,
            radius=args.radius,
            max_results=args.max_results,
            page_delay=args.page_delay,
        )
        print_places(places)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
