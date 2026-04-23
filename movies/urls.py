from django.urls import path
from . import views  # Usaremos 'views.nombre' para que sea más claro y organizado

urlpatterns = [
    # Rutas Principales
    path('', views.index, name='index'),
    path('all/', views.all_movies, name='all_movies'),
    path('search/', views.search_movies, name='search_movies'),
    path('<int:movie_id>/', views.movie, name='movie'),
    
    # Colecciones y Mis Películas
    path('mis-peliculas/', views.mis_peliculas, name='mis_peliculas'),
    path('collections/', views.collections, name='collections'),
    
    # Reseñas
    path('movie_review/add/<int:movie_id>/', views.add_review, name='add_review'),
    path('movie_reviews/<int:movie_id>/', views.movie_reviews, name='movie_reviews'),
    
    # Gestión de "Mas" (Añadir/Quitar)
    path('movie_Mas/add/<int:movie_id>/', views.add_Mas, name='add_Mas'),
    path('movie_Mas/remove/<int:movie_id>/', views.remove_Mas, name='remove_Mas'),
    
    # Pruebas y Otros
    path('movie_prueba/add/<int:movie_id>/', views.add_prueba, name='add_prueba'),
    path('saludo/<int:veces>/', views.saludo, name='saludo'),
]