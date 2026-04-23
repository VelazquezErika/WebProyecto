from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('all/', all_movies),
    path('actor/<int:id>/', views.actor_detail, name='actor_detail'),
    path('<int:movie_id>/', movie),
    path('movie_review/add/<int:movie_id>/', add_review),
    path('movie_reviews/<int:movie_id>/', movie_reviews, name='movie_reviews'),
]