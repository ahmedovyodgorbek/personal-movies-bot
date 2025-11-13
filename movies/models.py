from django.db import models
import re
import uuid



def safe_title(title):
    return re.sub(r"[^a-zA-Z0-9_-]", '_', title[:30])


def image_upload_path(instance, filename):
    unique_id = uuid.uuid4()
    title = safe_title(instance.slug)
    return f"movie/__image__{title}"



class MovieGenres(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'movie_genres'
        verbose_name = 'Movie Genre'
        verbose_name_plural = 'Movie Genres'

class MovieActors(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'movie_actors'
        verbose_name = 'Movie Actor'
        verbose_name_plural = 'Movie Actors'


class Movies(models.Model):
    TYPE_CHOICES = [
        ('movie', 'Movie'),
        ('cartoon', 'Cartoon'),
        ('series', 'Series')
    ]

    title = models.CharField(max_length=128)
    slug = models.SlugField(null=True, blank=True, max_length=255)
    description = models.TextField(null=True, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    genres = models.ManyToManyField(MovieGenres, related_name='movies', blank=True)
    actors = models.ManyToManyField(MovieActors, related_name="movies", blank=True)
    telegram_link = models.URLField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to=image_upload_path, null=True, blank=True)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, default="movie")
    release_date = models.PositiveIntegerField(help_text="Release year, e.g. 2024") 
    duration = models.CharField(max_length=64, help_text="Enter duration like '2h 30m', '1h', or '45m'", null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.release_date})"


    def short_description(self):
        """Limit description to 100 chars."""
        if not self.description:
            return ""
        return self.description[:97] + "..." if len(self.description) > 100 else self.description

    def genre_list(self):
        """Return a comma-separated list of genres."""
        return ", ".join(g.title for g in self.genres.all())

    def actor_list(self):
        """Return a comma-separated list of actors."""
        return ", ".join(a.name for a in self.actors.all())
    
    class Meta:
        verbose_name = 'Movie'
        verbose_name_plural = "Movies"
