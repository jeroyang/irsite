import codecs
import resource
from tempfile import NamedTemporaryFile

from nltk import tokenize

from django.core.files import File
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect

from pubmed_fetcher.models import Article, Query
from project2.models import *

def index(request):
    collections = Query.objects.all().order_by('-id')[:10]
    query = request.GET.get('q', '')
    collection = int(request.GET.get('c', 0))
    if query:
        keywords = request.GET['q'].split(' ')
        result_pmids = set.intersection(*[PostingList.objects.get(token=keyword.lower()).get_pmids() for keyword in keywords])
        if collection != 0:
            result_pmids = set.intersection(result_pmids, Query.objects.get(id=collection).get_pmids())
        results = [(Article.objects.get(pmid=pmid), show_snippet(Article.objects.get(pmid=pmid).abstract, keywords)) for pmid in result_pmids]
        results_count = len(result_pmids)
        search_time = 0.23
        search_overview = "About %s results (Search time: %s secs)" % (results_count, search_time)
    else:
        pass

    return render_to_response('project2.html',locals(), context_instance=RequestContext(request))

def show_snippet(context, queries):
    """Return the shortest snippet containing all the query terms"""
    return "Snippets %s" % context

def train_spelling_corrector(request):
    """Training the word_corrector using big.txt in resources/
    save the model in resources/word_corrector_model.pickle"""
    sc = SpellingCorrector(txtfile=codecs.open('resources/big.txt'))
    sc.dump(open('resources/spelling_corrector.pickle', 'wb'))

    return HttpResponseRedirect(reverse('pubmed_fetcher.views.index'))

def build_index(request):
    """docstring for build_index"""
    resource.setrlimit(resource.RLIMIT_NOFILE, (1000,-1))
    largest_index_version = Article.objects.order_by('-index_version')[0].index_version 
    smallest_index_version = Article.objects.order_by('index_version')[0].index_version
    if largest_index_version == smallest_index_version:
        working_index = largest_index_version + 1
    else:
        working_index = largest_index_version
        
    for article in Article.objects.filter(index_version__lt=working_index):
        fulltext = "%s \n%s" % (article.title, article.abstract)
        tokens = set([token.lower() for sentence in tokenize.sent_tokenize(fulltext) for token in tokenize.word_tokenize(sentence) if len(token) > 1])
        dict_postings = dict()
        for token in tokens:
            if token not in dict_postings:
                dict_postings[token] = [article.pmid]
            else:
                dict_postings[token].append(article.pmid)
        # Save dic_postings
        for token in dict_postings:
            if len(PostingList.objects.filter(token=token))==0:
                PostingList(token=token).save()
            PostingList.objects.get(token=token).pickle_pmids(dict_postings[token])  
        article.index_version += 1
        article.save()      
    
    return HttpResponseRedirect(reverse('pubmed_fetcher.views.index'))