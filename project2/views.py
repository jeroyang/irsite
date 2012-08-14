from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
    collections = 'render_collections(request.GET)'
    
    
    searchbar = 'Search bar'
    
    
    
    results_count = 2000
    
    
    
    search_results = 'render_search_results()'
    return render_to_response('project2.html',locals(), context_instance=RequestContext(request))