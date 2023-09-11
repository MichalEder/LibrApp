from django import forms
from .models import Kniha, Uzivatel

class KnihaForm(forms.ModelForm):

    class Meta:
        model = Kniha
        fields = ['nazev', 'autor', 'rok_vydani', 'zanr', 'jazyk', 'ISBN10', 'ISBN13','majitel']

class VyhledavaniISBNForm(forms.Form):
    isbn = forms.CharField(label='ISBN', max_length=13, required=False)

