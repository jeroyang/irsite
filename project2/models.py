from django.db import models
from nltk import word_tokenize
from tempfile import NamedTemporaryFile
import cPickle as pickle
import re
import collections
from django.conf import settings
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name): 
        """
        Returns a filename that's tree on the target storage system,
        and available for new content to be write to.
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            self.delete(name)
        return name

class PostingList(models.Model):
    token = models.CharField(max_length=100, primary_key=True)
    document_frequency = models.PositiveIntegerField(null=True)
    
    def _pickle_filename(instance, filename):
        return 'project2/postings/%s.pickle' %  slugify(instance.token.encode('utf-8'))
        
    posting_pickle = models.FileField(upload_to=_pickle_filename, 
                            storage=OverwriteStorage(), 
                            default='project2/emptyset.pickle')

    def __unicode__(self):
        pmids = list(pickle.load(self.posting_pickle))
        pmids.sort()
        if len(pmids) > 13:
            pl = "%s..." % "->".join([str(x) for x in pmids[:13]])
        else:
            pl = "->".join([str(x) for x in pmids])
        return "%s (%s): %s" % (self.token, self.document_frequency, pl)
    
    def pickle_pmids(self, pmids):
        """Pickle the pmids into posting_pickle filefield"""
        with NamedTemporaryFile() as tmp_file:
            pmids = self.get_pmids().union(pmids)
            pickle.dump(pmids, tmp_file)
            self.posting_pickle.save('fn', File(tmp_file))
            self.document_frequency=len(pmids)
            self.save()
    
    def get_pmids(self):
        try:
            return pickle.load(self.posting_pickle)
        except:
            return set()
    
class SpellingCorrector(object):
    """A class of spelling corrector, the model can be imported from a pickle or trained from a text file."""
    def __init__(self, pickle_file=None, txtfile=None):
        self.alphabet = 'abcdefghijklmnopqrstubwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        if pickle_file == None and txtfile != None:
            self.train(txtfile)
        elif pickle_file != None:
            self.load(pickle_file)
        else:
            self.NWORDS = dict()
            
    def _words(self, text):
        return re.findall(r'[A-Za-z]\w+', text)
        
    def train(self, txtfile):
        """Train the model according a big text file which should contain million words."""
        model = collections.defaultdict(lambda:1)
        features = self._words(txtfile.read())
        for f in features:
            model[f] += 1
        self.NWORDS = dict(model)
    
    def dump(self, pickle_file):
        """Dump the trained model into a pickle file"""
        pickle.dump(self.NWORDS, pickle_file) 
        
    def load(self, pickle_file):
        """Load the model from pickle file"""
        self.NWORDS = pickle.load(pickle_file)
        
    def _edits1(self, word):
        splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes    = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1 ]
        replaces   = [a + c + b[1:] for a,b in splits for c in self.alphabet if b]
        inserts    = [a + c+ b for a, b in splits for c in self.alphabet]
        return set(deletes + transposes + replaces + inserts)
        
    def _known_edits2(self, word):
        return set(e2 for e1 in self._edits1(word) for e2 in self._edits1(e1) if e2 in self.NWORDS)
    
    def _known(self, words):
        return set(w for w in words if w in self.NWORDS)
    
    def correct(self, word):
        candidates = self._known([word]) or self._known(self._edits1(word)) or self._known_edits2(word) or [word]
        return max(candidates, key=self.NWORDS.get)