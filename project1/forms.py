from django import forms

class XmlForm(forms.Form):
    xml_file1 = forms.FileField(
        label='Select a file',
        help_text='Only Pubmed xml is accepted',
        required=False
    )
    xml_file2 = forms.FileField(
        label='Select a file',
        help_text='Only Pubmed xml is accepted',
        required=False
    )    