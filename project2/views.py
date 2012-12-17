import codecs
import resource
import time
from tempfile import NamedTemporaryFile

from nltk import tokenize

from django.core.files import File
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify
from pubmed_fetcher.models import Article, Query
from project2.models import *

def index(request):
    collections = Query.objects.all().order_by('-id')[:10]
    query = request.GET.get('q', '')
    collection = int(request.GET.get('c', 0))
    if query:
        sc = SpellingCorrector(pickle_file=open('resources/spelling_corrector.pickle'))
        keywords = request.GET['q'].split(' ')
        start_time = time.clock()
        new_keywords = [sc.correct(k) for k in keywords]
        if [k.lower() for k in keywords] != [n.lower() for n in new_keywords]:
            sc_message = " ".join(new_keywords)
        try:
            result_ids = set.intersection(*[PostingList.objects.get(token=keyword.lower()).get_ids() for keyword in new_keywords])
        except:
            result_ids = set()
        if collection != 0:
            result_ids = set.intersection(result_ids, Query.objects.get(id=collection).get_ids())

        results = [(Article.objects.get(id=id), show_snippet(Article.objects.get(id=id).abstract, keywords)) for id in result_ids]
        results_count = len(result_ids)
        search_time = time.clock() - start_time
        search_overview = "About %s results (Search time: %s secs)" % (results_count, search_time)
    else:
        pass

    return render_to_response('project2.html',locals(), context_instance=RequestContext(request))

def sent_tokenize(context):
    remove_chars = re.compile(r'["()]')
    remove_quote = re.compile(r'(^|\W)\'(.*)\'(\W|$)')
    sent_breaks = re.compile(r'([a-zA-Z])([.!?\n]+)')
    context = remove_chars.sub(' ', context) 
    context = remove_quote.sub(r' \2 ', context)
    context = sent_breaks.sub(r'\1 \2{{sent_break}}', context)
    output = [s.strip() for s in context.split('{{sent_break}}') if s != '']
    return output

def word_tokenize(sentence):
    return re.split(r'[,;:/]?\s+', sentence)

def normalize(token):
    return slugify(token).lower()

def show_snippet(context, queries):
    """Return the shortest snippet containing all the query terms"""
    return context[0:250]+"..."

def train_spelling_corrector(request):
    """Training the word_corrector using big.txt in resources/
    save the model in resources/word_corrector_model.pickle"""
    sc = SpellingCorrector(txtfile=codecs.open('resources/big.txt'))
    sc.dump(open('resources/spelling_corrector.pickle', 'wb'))

    return HttpResponseRedirect(reverse('pubmed_fetcher.views.index'))

def build_index(request):
    """docstring for build_index"""
    dict_postings = dict()
    if request.GET.get('rebuild', '') == 'true':
        for article in Article.objects.filter(indexed=True).order_by('id'):
            article.indexed = False
            article.save()
    
    for article in Article.objects.filter(indexed=False).order_by('id'):
        fulltext = "%s \n%s" % (article.title, article.abstract)
        tokens = set([normalize(token) for sentence in sent_tokenize(fulltext) for token in word_tokenize(sentence) if len(normalize(token)) > 1])

        for token in tokens:
            if token not in dict_postings:
                dict_postings[token] = [article.id]
            else:
                dict_postings[token].append(article.id)
        article.indexed = True
        article.save()
  
    # Wirte postings
    for token in dict_postings:
        if len(PostingList.objects.filter(token=token))==0:
            PostingList(token=token).save()
        PostingList.objects.get(token=token).pickle_ids(dict_postings[token])
        print dict_postings[token]
    return HttpResponseRedirect(reverse('pubmed_fetcher.views.index'))


