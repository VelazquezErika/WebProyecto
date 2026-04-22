from django.urls import path
from .views import *

urlpatterns = [
    path('all/', all_movies),
    path('<int:movie_id>/', movie),
    path('saludo/<int:veces>/', saludo),
    path('movie_review/add/<int:movie_id>/', add_review),
    path('movie_Mas/add/<int:movie_id>/', add_Mas),
    path('movie_prueba/add<int:movie_id>', add_prueba),
    path('movie_reviews/<int:movie_id>/', movie_reviews, name='movie_reviews'),
    path('search/', search_movies, name='search_movies'),#url para la busqueda de peliculas
    path('', index)
]