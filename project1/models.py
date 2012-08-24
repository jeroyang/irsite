from django.db import models
from django.core.files import File
from lxml import etree

class Xml(models.Model):
    xml_file = models.FileField(upload_to='project1/xml')
    def __unicode__(self):
        return "id %s" % self.id

