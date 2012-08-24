from django.db import models

class Query(models.Model):
    query_term = models.CharField(max_length=200)
    query_date = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.query_term
    
class Journal(models.Model):
    issn = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    isoabbr = models.CharField(max_length=200)
    previous_title = models.ForeignKey('self')
    def __unicode__(self):
        return '%s\t"%s"' % (self.issn, self.title)

class Article(models.Model):
    pmid = models.CharField(max_length=50, primary_key=True)
    full_xml = models.TextField()
    fetch_time = models.DateTimeField(auto_now=True)
    journal = models.TextField() # <Journal> element
    author_list = models.TextField() # <AuthorList> element
    title = models.CharField(max_length=200) #Plain text title
    abstract_text = models.TextField() #Plain text abstract
    
    def __unicode__(self):
        return '%s\t"%s"' % (self.pmid, self.title)

