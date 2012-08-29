from django.db import models
from nltk import word_tokenize
from tempfile import NamedTemporaryFile
import cPickle as pickle
import re
import collections
import os 
from base64 import urlsafe_b64encode as b64
from django.conf import settings
from django.core.files import File
from django.core.files.storage import FileSystemStorage

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


class PostingList(models.Model):
    token = models.CharField(max_length=200, primary_key=True)
    document_frequency = models.PositiveIntegerField(null=True)
    postings = models.FileField(upload_to='project2/postings', 
                            storage=OverwriteStorage(), blank=True)
    def __unicode__(self):
        return "%s (%s)" % (token, document_frequency)
        
    def pickle_postings(self, pmids, refresh=False):
        """Pcikele the postings into posting FileField"""
        if refresh == True or not self:
            pass
        else: 
            pmids = pickle.load(self.postings.open(mode='wb')).extend(pmids)
        with NamedTemporaryFile() as tmp_file:
            pickle.dump(pmids, tmp_file)
            pickle_file = File(tmp_file)
            self.postings.save("%s.pickle" % b64(self.token), pickle_file)
            self.document_frequency=len(pmids)
            self.save()
    
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