from django.db import models
from django.core.files import File


class Xml(models.Model):
    xml_file = models.FileField(upload_to='project1/xml')

