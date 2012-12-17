def load_to_cache():
    #modification
    import os
    import gzip
    import re
    from base64 import urlsafe_b64encode as b64
    
    gzfiles = [fn for fn in os.listdir('./resources/medline') if fn[-2:] == 'gz']
    re_article = re.compile(r'</?MedlineCitation( .+)?>')
    re_pmid = re.compile(r'<PMID.*?>(?P<pmid>\d+)</PMID>')
    for fn in gzfiles:
        with gzip.open('./resources/medline/%s' % fn) as xml:
            article_xml = ''
            pmid = ''
            in_article = False
            while 1:
                line = xml.readline()
                if not line:
                    break
                if not in_article and re_article.search(line):
                    in_article = True
                    article_xml += line
                elif re_article.search(line):
                    article_xml += line
                    cache_filename = find_cache_name(pmid)
                    with gzip.open('./resources/cache/%s' % cache_filename, 'a') as cache_file:
                        cache_file.write(article_xml)
                    in_article = False
                    article_xml = ''
                    pmid = ''
                elif in_article:
                    article_xml += line
                    pmid_match = re_pmid.search(line)
                    if pmid_match:
                        pmid = pmid_match.group('pmid')  
        os.rename('./resources/medline/%s' % fn, './resources/medline/%s.loaded' % fn)

def find_cache_name(pmid):
    filename_length = 4
    return "%s%s.xml.gz" % ("0" * (filename_length-len(pmid)), pmid[:filename_length])
    
load_to_cache()