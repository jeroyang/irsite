import re

class Document(object):
    
    def __init__(self, text):
        self.text = text
        
    def chr_count(self):
        return len(self.text)
    
    def word_count(self):
        return len(re.findall(r'[\w\']+(?=[ :"!,.\?\)-\}\]]|$)', self.text, re.M))
        
    def sentence_count(self):
        return len(re.findall(r'[A-Z0-9]..+?(?:[.!?\n]|$)', self.text, re.M))
    
    def word_vector(self):
        words = re.findall(r'[\w\']+(?=[ :"!,.\?\)-\}\]]|$)', self.text, re.M)
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

        