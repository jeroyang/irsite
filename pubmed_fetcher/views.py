from datetime import date
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from pubmed_fetcher.models import *

def index(request):
    if request.GET.has_key('query'): 
        selected_query = request.GET['query'] 
        if len(Query.objects.filter(query_term=selected_query)) == 0:
            query = Query(query_term=selected_query)
            query.save()
    else: 
        selected_collection = ''
        
    def update_collections(collection=None):
        """Qurey the local and web repository to update the article list of a specific or each query
           update the specific collection if a collection name is give, otherwise, update all collections"""
        if collection == None:
            for q in Query.objects.filter(query_term=selected_collection):
                update_collections(collection=query_term)
        else:
            pass
    
    queries = Query.objects.all().order_by('-id')[:10]
    return render_to_response('pubmed_fetcher.html',locals(), context_instance=RequestContext(request))
  

def load_articles(request):
    """Load all articles from the .gz collection in MEDLINE directory to database"""
    import os
    import gzip
    from lxml import etree
        
    gzfiles = [fn for fn in os.listdir('./medline') if fn[-2:] == 'gz']
    for fn in gzfiles:
        with gzip.open('./medline/%s' % fn) as xml:
            tree = etree.parse(xml)
            articles = tree.findall('.//MedlineCitation')

            for article in articles:
                
                def _element_safe(tag):
                    if article.find('.//%s' % tag) == None:
                        return etree.Element(tag)
                    else:
                        return article.find('.//%s' % tag)

                Article(pmid=article.findtext("PMID"),
                        full_xml=etree.tostring(article),
                        journal=etree.tostring(_element_safe('Journal')),
                        author_list=etree.tostring(_element_safe('AuthorList')),
                        title=article.findtext(".//ArticleTitle"),
                        abstract_text=article.findtext(".//AbstractText") or '').save()
            del articles
            del tree
        os.rename('./medline/%s' % fn, './medline/%s.loaded' % fn)
        
    return HttpResponseRedirect(reverse('pubmed_fetcher.views.index'))
