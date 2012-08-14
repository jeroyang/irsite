from django.db import models
from nltk import word_tokenize

class PostingList(models.Model):
    token = models.CharField(max_length=200)
    frequency = models.PositiveIntegerField()
    postings = models.FileField(upload_to='project2/postings_pickles_db')
    