def statistics(list_html):
    return """<section class="width4"><h2>Document statistics:</h2><div class="column width2 first grid-example"><p>%s</p></div><div class="column width2 grid-example"><p>%s</p></div></section>""" % (list_html[0], list_html[1])
	

def identical_words(html):
    return """<section class="width4"><h2>Identical words in both documents:</h2><div class="column width4 grid-example"><p>%s</p></div></section>""" % html
    
    
def results_of_comparison(html):
    return """<section class="width4"><h2>Results of comparison</h2><div class="column width2 first grid-example note"><p>%s</p><br/></div><div class="column width2 grid-example note"><p>%s</p><br/></div></section>""" % (html[0], html[1])
        

