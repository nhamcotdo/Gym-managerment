from django import forms
from django.db import models
from django.http import HttpResponseNotFound

# Create your models here.
class SearchForm(forms.Form):
    search = forms.CharField(label='Tìm kiếm', max_length=100, required=False)

    def clean_search(self, *args, **kwargs):
        search = self.cleaned_data.get('search')
        if search == '':
            raise forms.ValidationError('Please enter a name in search box')
        return search