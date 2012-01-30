from django import forms

class XmlForm(forms.Form):
    xml_file = forms.FileField(
        label='Select a file',
        help_text='Only Pubmed xml is accepted'
    )
        