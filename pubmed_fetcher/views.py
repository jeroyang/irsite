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
    return [str(pmid) for pmid in output]

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
        article_list.append(Article(pmid=article.findtext("PMID"),
                                    index_version=0,
                                    title=article.findtext(".//ArticleTitle"),
                                    abstract="\n".join([a.text or '' for a in article.findall('.//Abstract/*')]))
    Article.objects.bulk_create(article_list, batch_size=999)
    del tree

def _import_pmids(pmid_list):
    """fetch articles from pubmed according the pmid_list"""
    
    #First, try to load the corresponding cache file"""
    for pmid in pmid_list:
        _load_cache('./resources/cache/%s' % _find_cache_name(pmid))
    
    # Check whether the pmid_list are now in the database
    pmid_list = _unfetched_pmid(pmid_list)
    
    # Fetch the missing Articles remotely
    if len(pmid_list) > 0:
        url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
        post_data = [('db', 'pubmed'),
                     ('id', ','.join(pmid_list)),
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
    if request.GET.has_key('query'): 
        selected_query = request.GET['query']
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


def _load_cache(cache_path):
    """Load all articles from the .gz collection in cache directory to database"""
    import gzip

    with gzip.open(cache_path) as xml:
            _import_xml(xml)
    
    
def bigtxt_generator(request):
    """Save a big.txt file in resources directory 
    containing the tiltes and abstracts in database,
    for traning the spelling corrector"""

    samples = sample(Article.objects.all(), 30000)
    with codecs.open('resources/big.txt', 'w', encoding='utf-8') as bigtxt:
        for s in samples:
            bigtxt.write("%s\n%s\n" % (s.title, s.abstract_text))
    
    return HttpResponseRedirect(reverse('pubmed_fetcher.views.index'))

def _load_to_cache():
    import os
    import gzip
    import re
    
    gzfiles = [fn for fn in os.listdir('./resources/medline') if fn[-2:] == 'gz']
    re_article = re.compile(r'</?MedlineCitation( .+)?>')
    re_pmid = re.compile(r'<PMID.*?>(?P<pmid>\d+)</PMID>')
    for fn in gzfiles:
        with gzip.open('./resources/medline/%s' % fn) as xml:
            article_xml = ''
            pmid = ''
            in_article = False
            while 1:
                line = xml.readline()
                if not line:
                    break
                if not in_article and re_article.search(line):
                    in_article = True
                    article_xml += line
                elif re_article.search(line):
                    article_xml += line
                    cache_filename = _find_cache_name(pmid)
                    with gzip.open('./resources/cache/%s' % cache_filename, 'a') as cache_file:
                        cache_file.write(article_xml)
                    in_article = False
                    article_xml = ''
                    pmid = ''
                elif in_article:
                    article_xml += line
                    pmid_match = re_pmid.search(line)
                    if pmid_match:
                        pmid = pmid_match.group('pmid')  
        os.rename('./resources/medline/%s' % fn, './resources/medline/%s.loaded' % fn)

def _find_cache_name(pmid):
    filename_length = 4
    return "%s%s.xml.gz" % ("0" * (filename_length-len(pmid)), pmid[:filename_length])
        
        
        
        
        