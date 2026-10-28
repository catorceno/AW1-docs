from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator

class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

# Create your models here.
class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField('name', max_length=255)
    description = models.TextField('description', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = 'Género'
        verbose_name_plural = "Géneros"

class FilmWork(UUIDMixin, TimeStampedMixin):
    class Type(models.TextChoices):
        # nombre en el código = valor en la bd, texto en el admin
        MOVIE = 'movie', 'Película'
        TV_SHOW = 'tv_show', 'Serie'

    title = models.CharField('title', max_length=255)
    type = models.CharField('type', max_length=20, choices=Type.choices) # Type.choices -> muestra un desplegable en el admin
    rating = models.FloatField('rating', blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]) # sin null=True la bd no acepta la columna vacía
    description = models.TextField('description', blank=True)
    creation_date = models.DateField('creation_date', blank=True, null=True)

    genres = models.ManyToManyField(Genre, through='GenreFilmWork')
    personas = models.ManyToManyField('Person', through='PersonFilmWork')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = 'Película'
        verbose_name_plural = "Películas"

class GenreFilmWork(UUIDMixin):
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"

class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField('full_name', max_length=255)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = "content\".\"person"
        verbose_name = 'Persona'
        verbose_name = "Personas"

class PersonFilmWork(UUIDMixin):
    role = models.TextField('roles')
    created = models.DateTimeField(auto_now_add=True)

    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)

    class Meta:
        db_table = "content\".\"person_film_work"