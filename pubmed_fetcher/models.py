from django.db import models
from tempfile import NamedTemporaryFile
from django.core.files import File
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from base64 import urlsafe_b64encode as b64
import pickle
import os

class OverwriteStorage(FileSystemStorage):
    def get_avaliable_name(self, name): 
        """
        Returns a filename that's tree on the target storage system,
        and available for new content to be write to.
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exist(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

class Query(models.Model):
    query_term = models.CharField(max_length=200)
    query_date = models.DateTimeField(auto_now=True)
    document_frequency = models.PositiveIntegerField(null=True)
    postings = models.FileField(upload_to='pubmed_fetcher/query_postings', 
                            storage=OverwriteStorage(), blank=True)
    def __unicode__(self):
        return "%s %s (%s)" % (self.query_date, self.query_term, self.document_frequency)
    
    def pickle_postings(self, pmid_set):
        """Pcikele the postings into posting FileField"""
        with NamedTemporaryFile() as tmp_file:
            pickle.dump(pmid_set, tmp_file)
            pickle_file = File(tmp_file)
            self.postings.save("%s.pickle" % b64(self.query_term), pickle_file)
            self.save()
    
    def get_pmids(self):
        try:
            return pickle.load(self.postings)
        except:
            return set()

class Article(models.Model):
    pmid = models.PositiveIntegerField()
    indexed = models.BooleanField(default=False)
    fetch_time = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200) #Plain text title
    abstract = models.TextField() #Plain text abstract
    def __unicode__(self):
        return '%s\t%s' % (self.pmid, self.title)

