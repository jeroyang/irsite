Search Engine
=============

* Web-spider Homework for NCKU-WRDU course, 2012
* Author: 資訊工程-P78011167-楊家融-HW5
* email: jeroyang@gmail.com

##Deployment##

I cannot deploy this project on internet, please see my demonstration on youtube: http://youtu.be/11qZSrWJb4A

##Requirements##

1. Python, the programming language.
2. Django, a robust python-based framework for websites.
3. lxml, the fast XML/HTML parser in python.

##Structure of Index##

1. The reversed index was stored in a fold (under /media). In this fold, each file contained the posting list of a single token, and named as [token].pickle.
2. The .pickle file is a sketch of python buildin structure of list.

##Processing in Query##

After a query was given, the engine separate this query into a list of tokens. According to tokens, the engine allocates the posting lists of each token, and find the intersections of them and return the document_ids. Therefore, find the titles corresponding to the document_ids, and show a shortened snippet of the fulltexts. 

##Problems##

1. Results sorting: Not yet implemented.
2. Relative small size of included documents: about 30,000 documents only. 
