from nose.tools import *
from project1.view import *

def test_statistics():
    statistics_list = ["<ul><li>Charactars:12</li><li>Words: 31</li><li>Sentences: 5</li></ul>", "<ul><li>Charactars:12</li><li>Words: 31</li><li>Sentences: 5</li></ul>"]
    assert_equal(statistics(statistics_list), """<section class="width4"><h2>Document statistics:</h2><div class="column width2 first grid-example"><p><ul><li>Charactars:12</li><li>Words: 31</li><li>Sentences: 5</li></ul></p></div><div class="column width2 grid-example"><p><ul><li>Charactars:12</li><li>Words: 31</li><li>Sentences: 5</li></ul></p></div></section>""")


def test_identical_words():
    common_word_html = '<span class="word_This">This</span> <span class="word_is">is</span>'
    assert_equal(identical_words(common_word_html), """<section class="width4"><h2>Identical words in both documents:</h2><div class="column width4 grid-example"><p><span class="word_This">This</span> <span class="word_is">is</span></p></div></section>""")


def test_results_of_comparison():
    document_list_html = ['<span class="word_This">This</span> <span class="word_is">is</span> a book.', 
                          '<span class="word_This">This</span> <span class="word_is">is</span> an ant.']
    assert_equal(results_of_comparison(document_list_html), """<section class="width4"><h2>Results of comparison</h2><div class="column width2 first grid-example note"><p><span class="word_This">This</span> <span class="word_is">is</span> a book.</p><br/></div><div class="column width2 grid-example note"><p><span class="word_This">This</span> <span class="word_is">is</span> an ant.</p><br/></div></section>""")