from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse , HttpResponseRedirect
from movies.models import Movie, MovieReview, Person
from movies.forms import MovieReviewForm, MovieMasCommentForm

def actor_detail(request, id):
    actor = get_object_or_404(Person, id=id)
    movies = actor.movie_credits.all()

    return render(request, 'movies/actor_detail.html', {
        'actor': actor,
        'movies': movies
    })

def all_movies(request):
    movies = Movie.objects.all()
    context = { 'objetos': movies, 'message': 'welcome' }
    return render(request, 'movies/allmovies.html', context=context)

def index(request):
    movies = Movie.objects.order_by('-release_date')[:8]
    context = { 'movies': movies, 'message': 'welcome' }
    return render(request, 'movies/index.html', context=context)

def movie(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    review_form = MovieReviewForm()
    print(request)
    print(movie.title)
    context = { 'movie':movie, 'saludo':'welcome', 'review_form':review_form, 'lista':[1,2,3,3,3] }
    return render(request,'movies/movie.html', context=context )

def movie_reviews(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    return render(request,'movies/reviews.html', context={'movie':movie} )

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