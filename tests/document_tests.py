from nose.tools import *
from project1.document import Document

def test_Document():
    str1 = "Hello, my name is Jerome. I am working on this project of IR class. There is no problem I cannot slove. I'm pretty sure. \nDon't you?"
    doc1 = Document(str1)
    
    assert_equal(doc1.text, str1)
    assert_equal(doc1.chr_count(), 132)
    assert_equal(doc1.word_count(), 26)
    assert_equal(doc1.sentence_count(), 5)
    
    str2 = "I love you, you love me, we love our children."
    doc2 = Document(str2)
    
    assert_equal(doc2.word_set(), set(['I', 'children', 'love', 'me', 'our', 'we', 'you' ]))
    assert_equal(doc2.word_vector(), {'children' : 1, 
                                    'I': 1,
                                    'love': 3,
                                    'me' : 1,
                                    'our' : 1,
                                    'you' : 2,
                                    'we' : 1})
    


    