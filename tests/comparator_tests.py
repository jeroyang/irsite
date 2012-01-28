from nose.tools import *
from project1.comparator import Comparator
from project1.document import Document

doc1 = Document("John is a secret agent.")
doc2 = Document("Mary is a secret agent, too.")
my_comparator = Comparator(doc1, doc2)

def test_Comparator():
    assert_equal(my_comparator.common_word_set(), set(['is', 'a', 'secret', 'agent']))
    
def test_common_word_html():
    assert_equal(my_comparator.common_word_html("word_"), '<span class="word_%s">%s</span> ' % ('a', 'a')+\
                                               '<span class="word_%s">%s</span> ' % ('agent', 'agent')+\
                                               '<span class="word_%s">%s</span> ' % ('is', 'is')+\
                                               '<span class="word_%s">%s</span>' % ('secret', 'secret'))
                                               
def test_text_list():
    assert_equal(my_comparator.text_list(), ["John is a secret agent.", "Mary is a secret agent, too."])

def test_document_list_html():
    assert_equal(my_comparator.document_list_html("word_"),[\
    'John <span class="word_is">is</span> <span class="word_a">a</span> <span class="word_secret">secret</span> <span class="word_agent">agent</span>.',
    'Mary <span class="word_is">is</span> <span class="word_a">a</span> <span class="word_secret">secret</span> <span class="word_agent">agent</span>, too.'\
    ])

def test_docuemnt_list_html_special():
    doc3 = Document("P&G is a large company.")
    doc4 = Document("Microsoft was small company at first.")
    doc5 = Document("company")
    my_comparator2 = Comparator(doc3, doc4, doc5)
    assert_equal(my_comparator2.document_list_html("word_"), [\
    'P&amp;G is a large <span class="word_company">company</span>.',
    'Microsoft was small <span class="word_company">company</span> at first.',
    '<span class="word_company">company</span>'])

def test_statistics_list_html():
    assert_equal(my_comparator.statistics_list_html(), ["<ul><li>Charactars: 23</li><li>Words: 5</li><li>Sentences: 1</li></ul>\n",\
                                                   "<ul><li>Charactars: 28</li><li>Words: 6</li><li>Sentences: 1</li></ul>\n"])
    

    