from nose.tools import *
from project2.models import *

def test_dictionary_compressor():
    tokens = ['automata', 'automate', 'automatic', 'automation']
    assert_equal(DictionaryCompressor(tokens), '8automate*a1\te2\tic3\tion')
    

    