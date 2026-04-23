import os
import environ
import requests
import psycopg2
from datetime import datetime, date, timezone
import sys

def add_movie(movie_id):
    env = environ.Env()
    environ.Env.read_env('.env')

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {env('API_TOKEN')}"
    }

    url_tmdb = f'https://api.themoviedb.org/3/movie/{movie_id}?language=es-MX'
    r = requests.get(url_tmdb, headers=headers)
    m = r.json()

    if 'title' not in m:
        print(f"Error en API TMDB: {m.get('status_message', 'No se encontró la película')}")
        return

    conn = psycopg2.connect(
        dbname=env('DB_NAME'),
        user=env('DB_USER'),
        password=env('DB_PASSWORD'),
        host=env('DB_HOST'),
        port=env('DB_PORT')
    )
    cur = conn.cursor()

    # créditos
    r_credits = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/credits?language=es-MX', headers=headers)
    credits_data = r_credits.json()
    cast_data = credits_data.get('cast', [])
    crew_data = credits_data.get('crew', [])
    actors = [(actor['name'], actor['known_for_department']) for actor in cast_data[:10]]
    crew = [(job['name'], job['job']) for job in crew_data[:15]]
    credits_list = actors + crew

    # jobs
    jobs = set([job for person, job in credits_list])
    if jobs:
        cur.execute('SELECT id, name FROM movies_job WHERE name IN %s', (tuple(jobs),))
        jobs_in_db = [row[1] for row in cur.fetchall()]
        jobs_to_create = [(name,) for name in jobs if name not in jobs_in_db]
        if jobs_to_create:
            cur.executemany('INSERT INTO movies_job (name) VALUES (%s)', jobs_to_create)

    # persons
    persons = set([person for person, job in credits_list])
    if persons:
        cur.execute('SELECT id, name FROM movies_person WHERE name IN %s', (tuple(persons),))
        persons_in_db = [row[1] for row in cur.fetchall()]
        persons_to_create = [(name,) for name in persons if name not in persons_in_db]
        if persons_to_create:
            cur.executemany('INSERT INTO movies_person (name) VALUES (%s)', persons_to_create)

    # genres
    genres = [d['name'] for d in m.get('genres', [])]
    if genres:
        cur.execute('SELECT id, name FROM movies_genre WHERE name IN %s', (tuple(genres),))
        genres_in_db = [row[1] for row in cur.fetchall()]
        genres_to_create = [(name,) for name in genres if name not in genres_in_db]
        if genres_to_create:
            cur.executemany('INSERT INTO movies_genre (name) VALUES