from django.shortcuts import render
from django.http import HttpResponse , HttpResponseRedirect
from movies.models import Movie, MovieReview, Person, MovieMas, MoviePrueba
from movies.forms import MovieReviewForm, MovieMasCommentForm
from django.db.models import Q

# Create your views here.
def search_movies(request):
    query = request.GET.get('q', '')
    
    if query:
        # Filtramos por título (title) o descripción (overview)
        # Nota: En tu modelo es 'overview', no 'description'
        results = Movie.objects.filter(
            Q(title__icontains=query) | Q(overview__icontains=query)
        )
    else:
        results = Movie.objects.none()

    return render(request, 'movies/search_results.html', {
        'results': results,
        'query': query
    })

def all_movies(request):
    movies = Movie.objects.all() #Movies de la DB
    context = { 'objetos': movies, 'message': 'welcome' }
    return render(request, 'movies/allmovies.html', context=context)

def index(request):
    movies = Movie.objects.all()
    context = { 'movies':movies, 'message':'welcome' }
    return render(request,'movies/index.html', context=context )
    
def saludo(request, veces):
    saludo = ' HOLA ' * veces
    personas = Person.objects.all()
    context = {'saludo':saludo, 'lista':[personas]}
    return render(request,'movies/saludo.html', context=context)

def movie(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    review_form = MovieReviewForm()
    print(request)
    print(movie.title)
    context = { 'movie':movie, 'saludo':'welcome', 'review_form':review_form, 'lista':[1,2,3,3,3] }
    return render(request,'movies/movie.html', context=context )

def movie_reviews(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    return render(request,'movies/reviews.html', context={'movie':movie } )
    
def add_Mas(request, movie_id):
    form = None
    movie = Movie.objects.get(id=movie_id)
    if request.method == 'POST':
        form = MovieMasCommentForm(request.POST)
        if form.is_valid():
            review = form.cleaned_data['review']
            movie_Mas = MovieMasCommentForm(
                    movie=movie,
                    review=review,
                    user=request.user)
            movie_like.save()
            return HttpResponseRedirect('/movies/')
    else:
        form = MovieMasCommentForm()
        return render(request,
                  'movies/movie_MasComment_form.html',
                  {'form': form, 'movie':movie})

def add_prueba(request, movie_id):
    form = None
    movie = Movie.objects.get(id=movie_id)
    if request.method == 'POST':
        form = MoviePruebaForm(request.POST)
        if form.is_valid():
            review = form.cleaned_data['review']
            movie_Mas = MoviePrueba(
                    movie=movie,
                    review=review,
                    user=request.user)
            movie_like.save()
            return HttpResponseRedirect('/movies/')
    else:
        form = MoviePruebaForm()
        return render(request,
                  'movies/movie_MasComment_form.html',
                  {'form': form, 'movie':movie})

def add_review(request, movie_id):
    form = None
    movie = Movie.objects.get(id=movie_id)
    if request.method == 'POST':
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            title  = form.cleaned_data['title']
            review = form.cleaned_data['review']
            movie_review = MovieReview(
                    movie=movie,
                    rating=rating,
                    title=title,
                    review=review,
                    user=request.user)
            movie_review.save()
            return HttpResponse(status=204,
                                headers={'HX-Trigger': 'listChanged'})
    else:
        form = MovieReviewForm()
        return render(request,
                  'movies/movie_review_form.html',
                  {'movie_review_form': form, 'movie':movie})