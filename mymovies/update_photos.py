import django
import os
import sys
import requests

# Ajusta esto al nombre de tu proyecto
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

sin_foto = Person.objects.filter(photo_url__isnull=True) | Person.objects.filter(photo_url='')
total = sin_foto.count()
print(f"Actores sin foto: {total}")

for i, person in enumerate(sin_foto, 1):
    try:
        r = requests.get(
            f'https://api.themoviedb.org/3/search/person?query={person.name}&language=es-MX',
            headers=headers
        )
        results = r.json().get('results', [])
        if results and results[0].get('profile_path'):
            person.photo_url = results[0]['profile_path']
            person.save()
            print(f"[{i}/{total}] ✓ {person.name}")
        else:
            print(f"[{i}/{total}] ✗ Sin foto: {person.name}")
    except Exception as e:
        print(f"[{i}/{total}] Error con {person.name}: {e}")

print("¡Listo!")