from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

from project1.models import Xml, XmlDocument, Comparator
from project1.forms import XmlForm

def index(request):
    # Handle file upload
    if request.method == 'POST':
        form = XmlForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Xml(xml_file=request.FILES['xml_file'])
            newdoc.save()
            
            # Redirect to the index after POST
            return HttpResponseRedirect(reverse('project1.views.index'))
    else:        
        xml_list = Xml.objects.all().order_by('-id')[:2]
        xml_document = list([XmlDocument(xml) for xml in xml_list])
        my_comparator = Comparator(*xml_document)

        common_word_html = my_comparator.common_word_html('word_')
    
        title_0 = xml_document[0].title
        author_0 = ''
        journal_0 = xml_document[0].journal
        year_0 = xml_document[0].year
        document_list_0 = my_comparator.document_list_html('word_')[0]
        statistics_list_0 = my_comparator.statistics_list_html()[0]
    
        title_1 = xml_document[1].title
        author_1 = ''
        journal_1 = xml_document[1].journal
        year_1 = xml_document[1].year
        document_list_1 = my_comparator.document_list_html('word_')[1]
        statistics_list_1 = my_comparator.statistics_list_html()[1]

        return render_to_response('project1.html',locals(),context_instance=RequestContext(request))
    