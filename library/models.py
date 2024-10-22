from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

class CustomUser(AbstractUser):
    # Additional fields can be added here if needed
    pass

    class Meta:
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

class LibraryShelf(models.Model):
    shelf_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.shelf_name

class Writer(models.Model):
    given_name = models.CharField(max_length=100, db_index=True)
    surname = models.CharField(max_length=100, db_index=True)
    birth_date = models.DateField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['given_name', 'surname']),
        ]

    def __str__(self):
        return f"{self.given_name} {self.surname}"

class Publication(models.Model):
    book_title = models.CharField(max_length=255)
    book_isbn = models.CharField(max_length=13, blank=True, null=True)
    associated_shelves = models.ManyToManyField(LibraryShelf, related_name='publications', blank=True)
    book_isbn13 = models.CharField(max_length=13, blank=True, null=True)
    language_of_book = models.CharField(max_length=50, blank=True, null=True)
    avg_rating = models.FloatField(blank=True, null=True)
    format_of_book = models.CharField(max_length=50, blank=True, null=True)
    total_pages = models.IntegerField(blank=True, null=True)
    book_publisher = models.CharField(max_length=255, blank=True, null=True)
    pub_date = models.CharField(max_length=50, blank=True, null=True)
    book_description = models.TextField(blank=True)
    cover_image_url = models.URLField(max_length=500, blank=True, null=True)
    writers = models.ManyToManyField(Writer)
    vector_tfidf = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['book_title']),
            models.Index(fields=['book_isbn']),
        ]

    def __str__(self):
        return self.book_title


class UserFavorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_favorites')
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'publication')
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.user.username} - {self.publication.book_title}"

class PublicationSimilarity(models.Model):
    pub1 = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='similarities_from_pub')
    pub2 = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='similarities_to_pub')
    similarity_score = models.FloatField()

    class Meta:
        unique_together = ('pub1', 'pub2')
        indexes = [
            models.Index(fields=['pub1', 'similarity_score']),
            models.Index(fields=['pub2', 'similarity_score']),
        ]

    def __str__(self):
        return f"Similarity between {self.pub1} and {self.pub2}: {self.similarity_score}"
