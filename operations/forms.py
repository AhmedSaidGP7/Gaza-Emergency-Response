from django import forms
from GazaResponse.models import *
from multiupload.fields import MultiFileField
from . import views


class DocumentForm(forms.ModelForm):
    document = MultiFileField(min_num=1, max_num=50, max_file_size=1024*1024*5)  # حدّد العدد الأقصى للملفات والحجم الأقصى لكل ملف

    class Meta:
        model = UploadedDocument
        fields = ['document']


class ManualDocumentForm(forms.Form):
    names = forms.ModelMultipleChoiceField(queryset=Person.objects.all(), required=True, widget=forms.SelectMultiple(attrs={'class': 'form-control js-example-basic-multiple'}))
    documents = MultiFileField(min_num=1, max_num=10, max_file_size=1024*1024*5) 