# ValueFinder - Sprint 1 (Google Places API New)

Script base en Python para buscar negocios en una zona con **Google Places API (New)**, con paginación y salida legible por consola.

## 1) Configuración en Google Cloud

1. Entra a [Google Cloud Console](https://console.cloud.google.com/).
2. Crea un proyecto nuevo (por ejemplo: `valuefinder-places`).
3. Activa billing:
   - Menú **Billing** → vincula una cuenta de facturación al proyecto.
4. Habilita APIs:
   - Ve a **APIs & Services** → **Library**.
   - Habilita **Places API** (la versión nueva usa endpoints `places.googleapis.com/v1/...`).
5. Crea la API Key:
   - **APIs & Services** → **Credentials** → **Create Credentials** → **API key**.
6. Restringe la key (recomendado):
   - **Application restrictions**: por IP o según tu entorno.
   - **API restrictions**: permitir solo **Places API**.

> Si billing no está activo, las llamadas a Places fallarán aunque la API key exista.

## 2) Setup local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env y pega tu key
```

## 3) Ejecución

Ejemplo (cafeterías en Madrid centro):

```bash
python places_sprint1.py \
  --query "cafe" \
  --lat 40.4168 \
  --lng -3.7038 \
  --radius 2000 \
  --max-results 60
```

También puedes pasar la key por argumento:

```bash
python places_sprint1.py --query "restaurant" --lat 40.4168 --lng -3.7038 --api-key "TU_KEY"
```

## 4) Campos solicitados (field mask)

El script pide explícitamente:

- `places.displayName` → nombre
- `places.formattedAddress` → dirección
- `places.id` → equivalente práctico a `place_id`
- `places.rating`
- `places.userRatingCount` → equivalente a `user_ratings_total`
- `places.websiteUri`
- `places.nationalPhoneNumber`
- `places.googleMapsUri` → enlace a Google Maps
- `places.location` → lat/lng
- `places.businessStatus`
- `nextPageToken` → paginación

## 5) Notas de paginación y límites

- Cada página trae hasta 20 lugares.
- Se usa `nextPageToken` para iterar páginas hasta `--max-results` (por defecto 60).
- Se incluye una pausa configurable (`--page-delay`, default 2 segundos) entre páginas.

## 6) Reglas clave para próximos sprints

- Places API no filtra directamente por "sin reseñas" en búsqueda: se filtra después.
- `userRatingCount` es el dato clave para detectar negocios con pocas o cero reseñas.
- Place Details y almacenamiento SQLite se implementarán en Sprint 2.
