import codecs
from tempfile import NamedTemporaryFile

from nltk import tokenize

from django.core.files import File
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect

from pubmed_fetcher.models import Article
from project2.models import *

def index(request):
    queries = 'render_collections(request.GET)'
    
    searchbar = 'Search bar'
    results_count = 2000
    search_time = 0.23
    
    search_overview = "About %s results (Search time: %s secs)" % (results_count, search_time)
    search_results = 'render_search_results()'
    return render_to_response('project2.html',locals(), context_instance=RequestContext(request))
    
def train_spelling_corrector(request):
    """Training the word_corrector using big.txt in resources/
    save the model in resources/word_corrector_model.pickle"""
    sc = SpellingCorrector(txtfile=codecs.open('resources/big.txt'))
    sc.dump(open('resources/spelling_corrector.pickle', 'wb'))

    return HttpResponseRedirect(reverse('pubmed_fetcher.views.index'))

def build_index(request):
    """docstring for build_index"""
    largest_index_version = Article.objects.order_by('-index_version')[0].index_version 
    smallest_index_version = Article.objects.order_by('index_version')[0].index_version
    if largest_index_version == smallest_index_version:
        working_index = largest_index_version + 1
    else:
        working_index = largest_index_version
        
    for article in Article.objects.filter(index_version__lt=working_index):
        fulltext = "%s \n%s" % (article.title, article.abstract)
        tokens = set([token for sentence in tokenize.sent_tokenize(fulltext) for token in tokenize.word_tokenize(sentence) if len(token) > 1])
        for token in tokens:
            posting_lists = PostingList.objects.filter(token=token)
            if len(posting_lists) == 0:
                posting_list = PostingList(token=token, document_frequency=1)
            else: 
                posting_list = posting_lists[0]
            posting_list.pickle_postings(set(article.pmid))
    
    return HttpResponseRedirect(reverse('pubmed_fetcher.views.index'))