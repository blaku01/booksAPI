from datetime import date
from django.db import models

# Create your models here.

class Author(models.Model):
    full_name = models.CharField(max_length=32)
    
class Book(models.Model):
    external_id = models.CharField(max_length=12, unique=True)
    title = models.CharField(max_length=350)
    authors = models.ManyToManyField(Author) # reconsider using charfield
    published_year = models.CharField(max_length=4) # takes around 4 bytes // SmallIntegerField (~2bytes) might be a better idea
    acquired = models.BooleanField(default=False)
    thumbnail = models.URLField()

    def __str__(self):
        return self.title
