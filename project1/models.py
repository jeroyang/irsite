from django.db import models
from document import Document
from lxml import etree
from django.core.files import File
import re
import cgi

class Xml(models.Model):
    xml_file = models.FileField(upload_to='project1/xml')

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

    def common_word_html(self, prefix='word_'):
        escaped_word_list = map(lambda x:cgi.escape(x), list(self.common_word_set()))
        escaped_word_list.sort()
        result = map(lambda x:'<span class="%s%s">%s</span>' % (cgi.escape(prefix), x, x), escaped_word_list)
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
