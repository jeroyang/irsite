import re

class Document(object):
    
    def __init__(self, text):
        self.text = text
        
    def chr_count(self):
        remove_newlines = re.sub(r'[\n\r]', r'', self.text, re.U | re.S)
        return len(remove_newlines)
    
    def word_count(self):
        remove_digits = re.sub(r'(\d{1,3}(,\d{3}|\d)*(\.\d+)?)', r'digits', self.text, re.U | re.M)
        return len(re.findall(r'[\w\']+(?=[ :"!,.\?\)-\}\]\n=<>]|$)', remove_digits, re.U | re.M))
        
    def sentence_count(self):
        remove_pair = re.sub(r'(\(.*?\)|\{.*?\}|\[.*?\]|\".*?\")', r'words_in_paired_marks', self.text, re.U | re.S) 
        return len(re.findall(r'[A-Z0-9]..+?(?:[.!?\n]|$)', remove_pair, re.U | re.M))
    
    def word_vector(self):
        words = re.findall(r'[\w\']+(?=[ :"!,.\?\)-\}\]\n=<>]|$)', self.text, re.M)
        words.sort()
        word_vector = {}
        for word in words:
            if not word in word_vector:
                word_vector[word] = 1
            else:
                word_vector[word] = word_vector[word] + 1
        return word_vector
    
    def word_set(self):
        return set(self.word_vector())

        