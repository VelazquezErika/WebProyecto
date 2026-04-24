from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class Genre(models.Model):
    name = models.CharField(max_length=80)
    
    def __str__(self):
        return self.name
    
class Person(models.Model):
    name = models.CharField(max_length=128)
    photo_url = models.CharField(max_length=255, blank=True, null=True)  # ← cambio aquí
    biography = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class Job(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=80)
    overview = models.TextField()
    release_date = models.DateField()
    running_time = models.IntegerField()
    budget = models.IntegerField(blank=True, null=True)
    tmdb_id = models.IntegerField(blank=True, null=True)
    revenue = models.IntegerField(blank=True, null=True)
    poster_path = models.URLField(blank=True, null=True)
    genres = models.ManyToManyField(Genre)
    credits = models.ManyToManyField(Person, through='MovieCredit')

    def __str__(self):
        return f'{self.title} {self.release_date}'


class MovieCredit(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='movie_credits')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_credits')
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    character = models.CharField(max_length=200, blank=True, null=True)

class MovieReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    review = models.TextField(blank=True)
    title = models.TextField(blank=False, null=False, default="Reseña")
class MovieMas(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    revierw = models.TextField(null=True, blank=True)
