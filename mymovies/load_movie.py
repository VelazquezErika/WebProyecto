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

    r_credits = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/credits?language=es-MX', headers=headers) 
    credits_data = r_credits.json()

    cast_data = credits_data.get('cast', [])
    crew_data = credits_data.get('crew', [])

    # Ahora guardamos también el profile_path
    actors = [(actor['name'], actor['known_for_department'], actor.get('profile_path') or '') for actor in cast_data[:10]]
    crew = [(job['name'], job['job'], '') for job in crew_data[:15]]
    credits_list = actors + crew

    # Jobs
    jobs = set([job for person, job, photo in credits_list])
    if jobs:
        cur.execute('SELECT id, name FROM movies_job WHERE name IN %s', (tuple(jobs),))
        jobs_in_db = [row[1] for row in cur.fetchall()]
        jobs_to_create = [(name,) for name in jobs if name not in jobs_in_db]
        if jobs_to_create:
            cur.executemany('INSERT INTO movies_job (name) VALUES (%s)', jobs_to_create)

    # Personas — ahora guarda photo_url
    persons = {name: photo for name, job, photo in credits_list}
    if persons:
        cur.execute('SELECT id, name FROM movies_person WHERE name IN %s', (tuple(persons.keys()),))
        persons_in_db = [row[1] for row in cur.fetchall()]
        persons_to_create = [(name, photo) for name, photo in persons.items() if name not in persons_in_db]
        if persons_to_create:
            cur.executemany('INSERT INTO movies_person (name, photo_url) VALUES (%s, %s)', persons_to_create)

    # Géneros
    genres = [d['name'] for d in m.get('genres', [])]
    if genres:
        cur.execute('SELECT id, name FROM movies_genre WHERE name IN %s', (tuple(genres),))
        genres_in_db = [row[1] for row in cur.fetchall()]
        genres_to_create = [(name,) for name in genres if name not in genres_in_db]
        if genres_to_create:
            cur.executemany('INSERT INTO movies_genre (name) VALUES (%s)', genres_to_create)

    # Película
    release_date_str = m.get('release_date')
    if release_date_str and release_date_str != "":
        date_obj = date.fromisoformat(release_date_str)
        date_time = datetime.combine(date_obj, datetime.min.time()).astimezone(timezone.utc)
    else:
        date_time = None

    sql_movie = '''INSERT INTO movies_movie 
                  (title, overview, release_date, running_time, budget, tmdb_id, revenue, poster_path) 
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;'''

    movie_values = (
        m.get('title', 'Sin Título'), 
        m.get('overview', ''), 
        date_time, 
        m.get('runtime', 0), 
        m.get('budget', 0), 
        movie_id, 
        m.get('revenue', 0), 
        m.get('poster_path', '')
    )
    
    cur.execute(sql_movie, movie_values)
    internal_movie_id = cur.fetchone()[0]
     
    if genres:
        sql_assign_genres = '''INSERT INTO movies_movie_genres (movie_id, genre_id)
                               SELECT %s, id FROM movies_genre WHERE name IN %s'''
        cur.execute(sql_assign_genres, (internal_movie_id, tuple(genres),))

    if credits_list:
        for credit_name, job_name, _ in credits_list:
            sql_credit = '''INSERT INTO movies_moviecredit (movie_id, person_id, job_id)
                            VALUES (
                                %s,
                                (SELECT id FROM movies_person WHERE name = %s LIMIT 1),
                                (SELECT id FROM movies_job WHERE name = %s LIMIT 1)
                            )'''
            cur.execute(sql_credit, (internal_movie_id, credit_name, job_name))

    conn.commit()
    print(f"¡Proceso completado con éxito! Película: {m.get('title')}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        add_movie(int(sys.argv[1]))
    else:
        print("Por favor, proporciona un ID de película de TMDB.")