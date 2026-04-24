from django.urls import path
from .views import *
from . import views

urlpatterns = [
    # Rutas Principales
    path('', views.index, name='index'),
    path('all/', views.all_movies, name='all_movies'),
    path('search/', views.search_movies, name='search_movies'),
    path('<int:movie_id>/', views.movie, name='movie'),
    path('actor/<int:actor_id>/', views.actor_detail, name='actor_detail'),
    
    # Colecciones y Mis Películas
    path('mis-peliculas/', views.mis_peliculas, name='mis_peliculas'),
    path('random/', views.random_movies, name='random_movies'),
    
    # Reseñas
    path('movie_review/add/<int:movie_id>/', views.add_review, name='add_review'),
    path('movie_reviews/<int:movie_id>/', views.movie_reviews, name='movie_reviews'),
    
    # Gestión de "Mas" (Añadir/Quitar)
    path('movie_Mas/add/<int:movie_id>/', views.add_Mas, name='add_Mas'),
    path('movie_Mas/remove/<int:movie_id>/', views.remove_Mas, name='remove_Mas'),
    
    # Pruebas y Otros
    path('movie_prueba/add/<int:movie_id>/', views.add_prueba, name='add_prueba'),
    path('saludo/<int:veces>/', views.saludo, name='saludo'),
    path('', views.index, name='index'),
    path('all/', all_movies),
    path('<int:movie_id>/', movie),
    path('movie_review/add/<int:movie_id>/', add_review),
    path('movie_reviews/<int:movie_id>/', movie_reviews, name='movie_reviews'),
]