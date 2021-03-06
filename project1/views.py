from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

from project1.models import Xml
from project1.forms import XmlForm

import re
import cgi
from lxml import etree
from math import floor

def index(request):
    # Handle file upload
    if request.method == 'POST':
        form = XmlForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                newdoc2 = Xml(xml_file=request.FILES['xml_file2'])
                newdoc2.save()
            except:
                pass
            try:
                newdoc1 = Xml(xml_file=request.FILES['xml_file1'])
                newdoc1.save()
            except:
                pass
        # Redirect to the index after POST
        return HttpResponseRedirect(reverse('project1.views.index'))
    else:        
        xml_list = Xml.objects.all().order_by('-id')[:2]
        xml_document = list([XmlDocument(xml) for xml in xml_list])
        my_comparator = Comparator(*xml_document)

        common_word_cloud = my_comparator.common_word_cloud()
    
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

        return render_to_response('project1.html',locals(), context_instance=RequestContext(request))
 

class Document(object):

    def __init__(self, text):
        self.text = text

    def chr_count(self):
        remove_newlines = re.sub(r'[\n\r]', r'', self.text, re.U | re.S)
        return len(remove_newlines)

    def word_count(self):
        remove_digits = re.sub(r'(\d{1,3}(,\d{3}|\d)*(\.\d+)?)', r'digits', self.text, re.U | re.M)
        return len(re.findall(r'[\w\']+(?=[ :"!,.\?\)-\}\]\n=<>]|$)', remove_digits, re.U | re.M))

    def sentence_count(self):
        remove_pair = re.sub(r'(\(.*?\)|\{.*?\}|\[.*?\]|\".*?\")', r'words_in_paired_marks', self.text, re.U | re.S) 
        return len(re.findall(r'[A-Z0-9]..+?(?:[.!?\n]|$)', remove_pair, re.U | re.M))

    def word_vector(self):
        words = re.findall(r'[\w\']+(?=[ :"!,.\?\)-\}\]\n=<>]|$)', self.text, re.M)
        words.sort()
        word_vector = {}
        for word in words:
            if not word in word_vector:
                word_vector[word] = 1
            else:
                word_vector[word] = word_vector[word] + 1
        return word_vector

    def word_set(self):
        return set(self.word_vector())

class XmlDocument(Document):
    def __init__(self, xml):
        _tree = etree.parse(xml.xml_file)
        self.text = _tree.xpath('//Article/Abstract/AbstractText')[0].text
        self.title = _tree.xpath('//Article/ArticleTitle')[0].text
        self.journal = _tree.xpath('//Article/Journal/Title')[0].text
        self.year = _tree.xpath('//Article/Journal/JournalIssue/PubDate/Year')[0].text

class Comparator(object):
    def __init__(self, *docs):
        self.document_list = docs

    def common_word_set(self):
        word_set_list = []
        for doc in self.document_list:
            word_set_list.append(doc.word_set())
        return set.intersection(*word_set_list)
        
    def common_word_vector(self):
        return dict([(word, min(list([doc.word_vector()[word] for doc in self.document_list]))) for word in self.common_word_set()])
        
    def common_word_html(self, prefix='word_'):
        escaped_word_list = map(lambda x:cgi.escape(x), list(self.common_word_set()))
        escaped_word_list.sort()
        result = map(lambda x:'<span class="%s%s">%s</span>' % (cgi.escape(prefix), x, x), escaped_word_list)
        return " ".join(result)
    
    def common_word_cloud(self, weight_levels=5, prefix='word_', weight='weight_'):
        escaped_word_list = map(lambda x:cgi.escape(x), list(self.common_word_set()))
        escaped_word_list.sort()
        word_counts = list([y for x,y in self.common_word_vector().iteritems()])
        word_counts.sort()
        word_size = len(word_counts)
        def word_to_weight(word):
            count = self.common_word_vector()[word]
            for i in range(weight_levels, 0, -1):
                if count >= word_counts[int((i - 1) * floor(word_size / weight_levels))]:
                    return i
            
        result = map(lambda x:'<span class="%s%s font-weight%d">%s</span>' % (cgi.escape(prefix), x, word_to_weight(x), x), escaped_word_list)
        return " ".join(result)

    def text_list(self):
        text_list=[]
        for doc in self.document_list:
            text_list.append(doc.text)
        return text_list

    def document_list_html(self, prefix='word_'):
        escaped_word_list = map(lambda x:cgi.escape(x), list(self.common_word_set()))
        escaped_text_list = map(lambda x:cgi.escape(x), self.text_list())
        escaped_text_list = map(lambda x:re.sub(r'(\W)', r'##\1\1##', x), escaped_text_list)
        list_html = map(lambda x:re.sub(r'(^|\W)('+'|'.join(escaped_word_list)+')(\W|$)' , r'\1<span class="%s\2">\2</span>\3' % prefix, x), escaped_text_list)
        return map(lambda x:re.sub(r'##(\W){2}##', r'\1', x), list_html)

    def statistics_list_html(self):
        return map(lambda x:"<ul><li>Charactars: %d</li><li>Words: %d</li><li>Sentences: %d</li></ul>" % (x.chr_count(), x.word_count(), x.sentence_count()), self.document_list)
  