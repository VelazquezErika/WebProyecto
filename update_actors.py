import django
import os
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mymovies.settings')
django.setup()

import environ
from movies.models import Person

env = environ.Env()
environ.Env.read_env('.env')

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {env('API_TOKEN')}"
}

# Trae todos los actores sin biografía
sin_bio = Person.objects.filter(biography__isnull=True) | Person.objects.filter(biography='')
total = sin_bio.count()
print(f"Actores sin biografía: {total}\n{'─'*40}")

for i, person in enumerate(sin_bio, 1):
    try:
        # Busca por nombre
        r = requests.get(
            f'https://api.themoviedb.org/3/search/person?query={person.name}&language=es-MX',
            headers=headers
        )
        results = r.json().get('results', [])

        if not results:
            print(f"[{i}/{total}] ✗ No encontrado: {person.name}")
            continue

        person_id = results[0]['id']

        # Trae detalle completo
        r2 = requests.get(
            f'https://api.themoviedb.org/3/person/{person_id}?language=es-MX',
            headers=headers
        )
        detail = r2.json()

        biography = detail.get('biography', '')
        photo = detail.get('profile_path', '')

        actualizado = False
        if biography:
            person.biography = biography
            actualizado = True
        if photo and not person.photo_url:
            person.photo_url = photo
            actualizado = True

        if actualizado:
            person.save()
            print(f"[{i}/{total}] ✓ {person.name}")
        else:
            print(f"[{i}/{total}] ⚠ Sin datos: {person.name}")

    except Exception as e:
        print(f"[{i}/{total}] ✗ Error con {person.name}: {e}")

print(f"\n{'─'*40}")
print("¡Listo!")
