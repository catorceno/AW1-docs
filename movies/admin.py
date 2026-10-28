from django.contrib import admin
from .models import Genre, GenreFilmWork, FilmWork, PersonFilmWork, Person

# Register your models here.
class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork

class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass

@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass