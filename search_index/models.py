from django.db import models

# Create your models here.

class Book(models.Model):
    bookName = models.CharField(max_length=200, null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    count_char = models.CharField(max_length=100, null=True, blank=True)
    cover = models.URLField(max_length=200, null=True, blank=True)
    authors = models.CharField(max_length=200, null=True, blank=True)
    count_click = models.CharField(max_length=50, null=True, blank=True)
    introduction = models.TextField(null=True, blank=True)
    sourceUrl = models.URLField(max_length=250, null=True, blank=True)
    sourceName = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    tag = models.CharField(max_length=255, null=True, blank=True)
    score = models.CharField(max_length=100, null=True, blank=True)




    class Meta:
        db_table = 'books'  # Ensure the table name matches the one in your database



    def __str__(self):
        return self.bookName
