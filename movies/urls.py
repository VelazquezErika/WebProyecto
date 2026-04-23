from django.urls import path
from . import views 

urlpatterns = [
    path('all/', views.all_movies),
    path('<int:movie_id>/', views.movie, name='movie'), 
    path('saludo/<int:veces>/', views.saludo),
    path('movie_review/add/<int:movie_id>/', views.add_review),
    path('movie_Mas/add/<int:movie_id>/', views.add_Mas, name='add_Mas'),
    path('movie_prueba/add/<int:movie_id>/', views.add_prueba),
    path('movie_reviews/<int:movie_id>/', views.movie_reviews, name='movie_reviews'),
    path('mis-peliculas/', views.mis_peliculas, name='mis_peliculas'),
    path('collections/', views.collections, name='collections'),
    path('movie_Mas/remove/<int:movie_id>/', views.remove_Mas, name='remove_Mas'),
    path('', views.index)
]