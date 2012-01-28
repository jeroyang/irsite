import re
import cgi
from document import Document

class Comparator(object):

    def __init__(self, *docs):
        self.document_list = docs
            
    def common_word_set(self):
        word_set_list = []
        for doc in self.document_list:
            word_set_list.append(doc.word_set())
        return set.intersection(*word_set_list)
        
    def common_word_html(self, prefix):
        escaped_word_list = map(lambda x:cgi.escape(x), list(self.common_word_set()))
        escaped_word_list.sort()
        result = map(lambda x:'<span class="%s%s">%s</span>' % (cgi.escape(prefix), x, x), escaped_word_list)
        return " ".join(result)
        
    def text_list(self):
        text_list=[]
        for doc in self.document_list:
            text_list.append(doc.text)
        return text_list
        
    def document_list_html(self, prefix):
        escaped_word_list = map(lambda x:cgi.escape(x), list(self.common_word_set()))
        escaped_text_list = map(lambda x:cgi.escape(x), self.text_list())
        return map(lambda x:re.sub(r'('+'|'.join(escaped_word_list)+')([^\w]|$)' , r'<span class="%s\1">\1</span>\2' % prefix, x, re.M), escaped_text_list)
        
    def statistics_list_html(self):
        return map(lambda x:"<ul><li>Charactars: %d</li><li>Words: %d</li><li>Sentences: %d</li></ul>\n" % (x.chr_count(), x.word_count(), x.sentence_count()), self.document_list)
        
    
        
      
        