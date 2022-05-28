from datetime import date
from django.db import models

# Create your models here.


class Author(models.Model):
    full_name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.full_name


class Book(models.Model):
    external_id = models.CharField(
        max_length=12, unique=True, null=True, default=None)
    title = models.CharField(max_length=350)
    authors = models.ManyToManyField(Author, blank=True)
    # takes 2 bytes // DateField & CharField would take around 4 bytes // reconsider
    published_year = models.SmallIntegerField(null=True)
    acquired = models.BooleanField(default=False)
    thumbnail = models.URLField(null=True, default=None)

    def __str__(self):
        return self.title
