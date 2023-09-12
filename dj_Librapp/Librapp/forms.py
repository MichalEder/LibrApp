from django import forms
from .models import Kniha, Uzivatel

class KnihaForm(forms.ModelForm):

    class Meta:
        model = Kniha
        fields = ['nazev', 'autor', 'rok_vydani', 'zanr', 'jazyk', 'ISBN10', 'ISBN13','majitel']

class VyhledavaniISBNForm(forms.Form):
    isbn = forms.CharField(label='ISBN', max_length=13, required=False)

class RegistraceForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Uzivatel
        fields = ['email', 'password', 'jmeno', 'prijmeni', 'uzivatelske_jmeno']

class LoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        fields = ['email', 'password']

