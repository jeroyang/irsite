from nose.tools import *
from pubmed_fetcher.views import _fetch_pubmed_ids

def test_fetch_pubmed_ids():
    pmids = ['22913682', '21782277', '21291843', '21120687', '20976537', '20422135', '20392356', '18581721', '18051214', '18034948', '16008166', '15837019', '15759822', '15544014', '15490023', '15302738', '15075019', '10820954', '9872036', '9840142', '10592814']
    assert_equal(_fetch_pubmed_ids('adult onset immunodeficiency taiwan'), pmids)
     