from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from movies.models import Movie, MovieReview, Person, MovieMas, MoviePrueba
from movies.forms import MovieReviewForm, MovieMasCommentForm


def all_movies(request):
    movies = Movie.objects.all()
    context = { 'objetos': movies, 'message': 'welcome' }
    return render(request, 'movies/allmovies.html', context=context)

def index(request):
    movies = Movie.objects.all()
    context = { 'movies': movies, 'message': 'welcome' }
    return render(request, 'movies/index.html', context=context)

def movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    review_form = MovieReviewForm()
    context = { 'movie': movie, 'review_form': review_form }
    return render(request, 'movies/movie.html', context=context)

def movie_reviews(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movies/reviews.html', context={'movie': movie})

@login_required
def mis_peliculas(request):

    favoritos = MovieMas.objects.filter(user=request.user).select_related('movie')
    movies = [f.movie for f in favoritos]
    
    context = {
        'objetos': movies,
        'message': 'Mis Películas Favoritas'
    }

    return render(request, 'movies/allmovies.html', context=context)

@login_required
def add_Mas(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':

        exists = MovieMas.objects.filter(user=request.user, movie=movie).exists()
        if not exists:
            MovieMas.objects.create(
                movie=movie,
                user=request.user,
                review="Le dio like"
            )

        return HttpResponseRedirect('/movies/mis-peliculas/')
    return HttpResponseRedirect(f'/movies/{movie_id}/')

@login_required
def add_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            movie_review = MovieReview(
                movie=movie,
                rating=form.cleaned_data['rating'],
                title=form.cleaned_data['title'],
                review=form.cleaned_data['review'],
                user=request.user
            )
            movie_review.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})
    else:
        form = MovieReviewForm()
    return render(request, 'movies/movie_review_form.html', {'movie_review_form': form, 'movie': movie})

def collections(request):

    return mis_peliculas(request)


def saludo(request, veces):
    saludo_str = ' HOLA ' * veces
    personas = Person.objects.all()
    context = {'saludo': saludo_str, 'lista': personas}
    return render(request, 'movies/saludo.html', context=context)


@login_required
def add_prueba(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        MoviePrueba.objects.create(
            movie=movie,
            user=request.user,
            review="Registro de prueba"
        )
        return HttpResponseRedirect('/movies/')

    return render(request, 'movies/movie_MasComment_form.html', {'movie': movie})


def saludo(request, veces):
    saludo_str = ' HOLA ' * veces
    personas = Person.objects.all()
    context = {'saludo': saludo_str, 'lista': personas}
    return render(request, 'movies/saludo.html', context=context)

@login_required
def add_Mas(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':

        obj, created = MovieMas.objects.get_or_create(
            movie=movie,
            user=request.user,
            defaults={'revierw': 'Like'} 
        )

        if not created and hasattr(obj, 'revierw') and not obj.revierw:
            obj.revierw = 'Like'
            obj.save()

        return HttpResponse(status=204)
    return HttpResponseRedirect(f'/movies/{movie_id}/')

@login_required
def remove_Mas(request, movie_id):
    if request.method == 'POST':

        movie = get_object_or_404(Movie, id=movie_id)
        like = MovieMas.objects.filter(user=request.user, movie=movie)
        
        if like.exists():
            like.delete()
        return HttpResponseRedirect('/movies/mis-peliculas/')
    
    return HttpResponseRedirect(f'/movies/{movie_id}/')
