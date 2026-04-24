import os
import environ
import requests
import psycopg2
from datetime import datetime, date, timezone
import random

def get_connection(env):
    return psycopg2.connect(
        dbname=env('DB_NAME'),
        user=env('DB_USER'),
        password=env('DB_PASSWORD'),
        host=env('DB_HOST'),
        port=env('DB_PORT')
    )

def add_movie(movie_id, headers, env):
    url_tmdb = f'https://api.themoviedb.org/3/movie/{movie_id}?language=es-MX'
    r = requests.get(url_tmdb, headers=headers)
    m = r.json()

    if 'title' not in m:
        print(f"  ✗ Error: {m.get('status_message', 'No se encontró')}")
        return False

    conn = get_connection(env)
    cur = conn.cursor()

    cur.execute('SELECT id FROM movies_movie WHERE tmdb_id = %s', (movie_id,))
    if cur.fetchone():
        print(f"  ⚠ Ya existe: {m.get('title')}")
        cur.close()
        conn.close()
        return False

    r_credits = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/credits?language=es-MX', headers=headers)
    credits_data = r_credits.json()
    cast_data = credits_data.get('cast', [])
    crew_data = credits_data.get('crew', [])

    actors = [(actor['name'], actor['known_for_department'], actor.get('profile_path') or '') for actor in cast_data[:10]]
    crew = [(job['name'], job['job'], '') for job in crew_data[:15]]
    credits_list = actors + crew

    jobs = set([job for person, job, photo in credits_list])
    if jobs:
        cur.execute('SELECT id, name FROM movies_job WHERE name IN %s', (tuple(jobs),))
        jobs_in_db = [row[1] for row in cur.fetchall()]
        jobs_to_create = [(name,) for name in jobs if name not in jobs_in_db]
        if jobs_to_create:
            cur.executemany('INSERT INTO movies_job (name) VALUES (%s)', jobs_to_create)

    persons = {name: photo for name, job, photo in credits_list}
    if persons:
        cur.execute('SELECT id, name FROM movies_person WHERE name IN %s', (tuple(persons.keys()),))
        persons_in_db = [row[1] for row in cur.fetchall()]
        persons_to_create = [(name, photo) for name, photo in persons.items() if name not in persons_in_db]
        if persons_to_create:
            cur.executemany('INSERT INTO movies_person (name, photo_url) VALUES (%s, %s)', persons_to_create)

    genres = [d['name'] for d in m.get('genres', [])]
    if genres:
        cur.execute('SELECT id, name FROM movies_genre WHERE name IN %s', (tuple(genres),))
        genres_in_db = [row[1] for row in cur.fetchall()]
        genres_to_create = [(name,) for name in genres if name not in genres_in_db]
        if genres_to_create:
            cur.executemany('INSERT INTO movies_genre (name) VALUES (%s)', genres_to_create)

    release_date_str = m.get('release_date')
    if release_date_str:
        date_obj = date.fromisoformat(release_date_str)
        date_time = datetime.combine(date_obj, datetime.min.time()).astimezone(timezone.utc)
    else:
        date_time = None

    cur.execute('''INSERT INTO movies_movie 
                  (title, overview, release_date, running_time, budget, tmdb_id, revenue, poster_path) 
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;''',
                (m.get('title', 'Sin Título'), m.get('overview', ''), date_time,
                 m.get('runtime', 0), m.get('budget', 0), movie_id,
                 m.get('revenue', 0), m.get('poster_path', '')))
    internal_movie_id = cur.fetchone()[0]

    if genres:
        cur.execute('''INSERT INTO movies_movie_genres (movie_id, genre_id)
                       SELECT %s, id FROM movies_genre WHERE name IN %s''',
                    (internal_movie_id, tuple(genres),))

    for credit_name, job_name, _ in credits_list:
        cur.execute('''INSERT INTO movies_moviecredit (movie_id, person_id, job_id)
                        VALUES (%s,
                            (SELECT id FROM movies_person WHERE name = %s LIMIT 1),
                            (SELECT id FROM movies_job WHERE name = %s LIMIT 1))''',
                    (internal_movie_id, credit_name, job_name))

    conn.commit()
    cur.close()
    conn.close()
    return True


def cargar_categoria(endpoint, headers, env):
    print(f"\nObteniendo películas...")
    r = requests.get(
        f'https://api.themoviedb.org/3/movie/{endpoint}?language=es-MX&page=1',
        headers=headers
    )
    movies = r.json().get('results', [])
    procesar_lista(movies, headers, env)


def cargar_aleatorias(headers, env):
    # TMDB tiene ~500 páginas en discover, elige páginas al azar
    paginas_random = random.sample(range(1, 500), 5)
    print(f"\nEligiendo películas de páginas aleatorias: {paginas_random}")

    todas = []
    for pagina in paginas_random:
        r = requests.get(
            f'https://api.themoviedb.org/3/discover/movie?language=es-MX&page={pagina}&sort_by=popularity.desc',
            headers=headers
        )
        results = r.json().get('results', [])
        todas.extend(results)

    # Mezcla los resultados y toma 20
    random.shuffle(todas)
    movies = todas[:20]
    print(f"→ {len(movies)} películas seleccionadas aleatoriamente")
    procesar_lista(movies, headers, env)


def procesar_lista(movies, headers, env):
    total = len(movies)
    exitosas = 0
    fallidas = 0
    ya_existian = 0

    print(f"→ {total} películas a procesar\n{'─'*40}")

    for i, movie in enumerate(movies, 1):
        print(f"[{i}/{total}] {movie['title']}...")
        try:
            ok = add_movie(movie['id'], headers, env)
            if ok:
                exitosas += 1
                print(f"  ✓ Cargada")
            else:
                ya_existian += 1
        except Exception as e:
            fallidas += 1
            print(f"  ✗ Error: {e}")

    print(f"\n{'─'*40}")
    print(f"✓ Nuevas:       {exitosas}")
    print(f"⚠ Ya existían: {ya_existian}")
    print(f"✗ Errores:      {fallidas}")


def mostrar_menu():
    categorias = {
        '1': ('popular',     'Populares ahora'),
        '2': ('top_rated',   'Mejor valoradas'),
        '3': ('now_playing', 'En cartelera'),
        '4': ('upcoming',    'Próximos estrenos'),
        '5': (None,          'Aleatorias 🎲'),
        '6': (None,          'Salir'),
    }

    print("\n╔══════════════════════════════╗")
    print("║   Cargar películas de TMDB   ║")
    print("╠══════════════════════════════╣")
    for key, (_, nombre) in categorias.items():
        print(f"║  [{key}] {nombre:<24}║")
    print("╚══════════════════════════════╝")

    while True:
        opcion = input("\nElige una categoría: ").strip()
        if opcion in categorias:
            return opcion, categorias
        print("Opción no válida, intenta de nuevo.")


def run():
    env = environ.Env()
    environ.Env.read_env('.env')
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {env('API_TOKEN')}"
    }

    while True:
        opcion, categorias = mostrar_menu()

        if opcion == '6':
            print("¡Hasta luego!")
            break
        elif opcion == '5':
            print("\nCargando: Aleatorias 🎲")
            cargar_aleatorias(headers, env)
        else:
            endpoint, nombre = categorias[opcion]
            print(f"\nCargando: {nombre}")
            cargar_categoria(endpoint, headers, env)

        otra = input("\n¿Cargar otra categoría? (s/n): ").strip().lower()
        if otra != 's':
            print("¡Listo!")
            break


if __name__ == "__main__":
    run()