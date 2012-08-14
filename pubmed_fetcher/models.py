from django.db import models

class Query(models.Model):
    query_term = models.CharField(max_length=200)
    query_date = models.DateTimeField('date queried')
    
class Journal(models.Model):
    issn = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    isoabbr = models.CharField(max_length=200)
    previous_title = models.ForeignKey('self')

class Article(models.Model):
    pmid = models.CharField(max_length=50)
    xml = models.TextField()
    fetch_date = models.DateTimeField('date fetched')
    query_term = models.ManyToManyField(Query)
    
    journal = models.ManyToManyField(Journal)
    volume = models.CharField(max_length=10)
    issue = models.CharField(max_length=10)
    pagination = models.CharField(max_length=10)
    pubdate = models.CharField(max_length=100)
    
    article_date = models.DateTimeField('date published')
    title = models.CharField(max_length=200)
    authors = models.CharField(max_length=600)
    abstract_text = models.TextField()
    pii = models.CharField(max_length=50)
    doi = models.CharField(max_length=50)
    pmc = models.CharField(max_length=50)
    

