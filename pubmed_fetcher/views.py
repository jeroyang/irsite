import codecs
from datetime import date
from random import sample
from urllib2 import urlopen
from urllib import quote_plus, urlencode
from lxml import etree
import pickle

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from pubmed_fetcher.models import *

def _fetch_pubmed_ids(query_term, ret_max=1024):
    ret_start = 0
    output = []

    while 1:
        url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s&retstart=%s&retmax=%s'\
        % (quote_plus(query_term), ret_start, ret_max)
        tree = etree.parse(urlopen(url))
            
        count = int(tree.xpath('/eSearchResult/Count/text()')[0])
        ret_max = int(tree.xpath('/eSearchResult/RetMax/text()')[0])
        output.extend(tree.xpath('/eSearchResult/IdList/Id/text()'))

        if ret_start + ret_max < count:
            ret_start += ret_max
        else:
            break
    return [int(pmid) for pmid in output]

def _import_xml(xml_file):
    """Import pubmed xml (local or remote file object) to database"""
    tree = etree.parse(xml_file)
    def _safe_find(tag, xmltree):
        if xmltree.find('.//%s' % tag) == None:
            return etree.Element(tag)
        else:
            return xmltree.find('.//%s' % tag)
    
    article_list = []
    for article in tree.findall('.//MedlineCitation'):
        article_list.append(Article(pmid=int(article.findtext("PMID")),
                                    title=article.findtext(".//ArticleTitle"),
                                    abstract="\n".join([a.text or '' for a in article.findall('.//Abstract/*')])))
        if len(article_list) >= 100:
            Article.objects.bulk_create(article_list)
            article_list = []
    Article.objects.bulk_create(article_list)
    del tree

def _import_pmids(pmid_list):
    """fetch articles from pubmed according the pmid_list"""
    if len(pmid_list) > 0:
        url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
        post_data = [('db', 'pubmed'),
                     ('id', ','.join([str(i) for i in pmid_list])),
                     ('retmode', 'xml')]
        xml = urlopen(url, urlencode(post_data))
        _import_xml(xml)
    
def _unfetched_pmid(pmid_list):
    """docstring for _unfetched_pmid"""
    unfetched_pmids = []
    for the_pmid in pmid_list:
        try:
            Article.objects.get(pmid=the_pmid)
        except: 
            unfetched_pmids.append(the_pmid)
    return unfetched_pmids

def index(request):
    if request.GET.has_key('c'): 
        selected_query = request.GET['c']
        pmids = _fetch_pubmed_ids(selected_query)
        _import_pmids(_unfetched_pmid(pmids))
        if len(Query.objects.filter(query_term=selected_query)) == 0:
            query = Query(query_term=selected_query, document_frequency=len(set(pmids)))
            query.pickle_postings(set(pmids))
            query.save()
    else: 
        selected_query = ''
        
    queries = Query.objects.all().order_by('-id')[:10]
    return render_to_response('pubmed_fetcher.html',locals(), context_instance=RequestContext(request))
  
def load_articles(request):
    """Load all articles from the .gz collection in MEDLINE directory to database"""
    import os
    import gzip

    gzfiles = [fn for fn in os.listdir('./resources/medline') if fn[-2:] == 'gz']
    for fn in gzfiles:
        with gzip.open('./resources/medline/%s' % fn) as xml:
            _import_xml(xml)
        os.rename('./resources/medline/%s' % fn, './resources/medline/%s.loaded' % fn)

    return HttpResponseRedirect(reverse('pubmed_fetcher.views.index'))
    
def bigtxt_generator(request):
    """Save a big.txt file in resources directory 
    containing the tiltes and abstracts in database,
    for traning the spelling corrector"""

    samples = sample(Article.objects.all(), 30000)
    with codecs.open('resources/big.txt', 'w', encoding='utf-8') as bigtxt:
        for s in samples:
            bigtxt.write("%s\n%s\n" % (s.title, s.abstract))
    
    return HttpResponseRedirect(reverse('pubmed_fetcher.views.index'))

        
        
        