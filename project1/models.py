from django.db import models
from comparator import Comparator
from document import Document

class Xml(models.Model):
    filename = models.CharField(max_length=200)
    upload_date = models.DateTimeField('date uploaded')
    file = models.FileField(upload_to='xml')
    
