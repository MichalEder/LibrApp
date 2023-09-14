from django.shortcuts import render, HttpResponse, redirect
from django.views import generic
from django.urls import reverse_lazy
from .models import Kniha, Uzivatel
from django.db.models import Q
from .forms import KnihaForm, VyhledavaniISBNForm, RegistraceForm, LoginForm
import requests
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

class UpravKnihu(generic.UpdateView):
    model = Kniha
    form = KnihaForm
    template_name = 'Librapp/uprav_knihu.html'
    fields = ['nazev', 'autor', 'rok_vydani', 'zanr', 'jazyk', 'ISBN10', 'ISBN13', 'majitel']

    def get_success_url(self):
        return reverse_lazy('detail', kwargs={'pk': self.object.id})


class UpravProfil(generic.UpdateView):
    model = Uzivatel
    form = RegistraceForm
    template_name = 'Librapp/uprav_profil.html'
    fields = ['email', 'jmeno', 'prijmeni', 'uzivatelske_jmeno']

    def get_success_url(self):
        return reverse_lazy('profil', kwargs={'pk': self.object.id})


class OdstranKnihu(generic.DeleteView):
    model = Kniha
    template_name = 'Librapp/odstran_knihu.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirmation_message'] = f"Opravdu si přejete smazat knihu {self.object.nazev}? "
        return context

    def get_success_url(self):
        user_id = self.request.user.id
        return reverse_lazy('profil', kwargs={'pk': user_id})


class OdstranUzivatele(generic.DeleteView):
    model = Uzivatel
    template_name = 'Librapp/odstran_uzivatele.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            'confirmation_message'] = f"Opravdu si přejete smazat účet uživatele {self.object.jmeno} {self.object.prijmeni}?"
        return context


class Detail(generic.DetailView):
    model = Kniha
    template_name = 'Librapp/detail.html'


class SeznamKnih(generic.ListView):
    template_name = "Librapp/index.html"
    context_object_name = "knihy"

    def get_queryset(self):

        query = self.request.GET.get('q')
        if query:
            return Kniha.objects.filter(
                Q(nazev__icontains=query) |
                Q(autor__icontains=query)
            ).order_by('-id')
        else:
            return Kniha.objects.all().order_by('-id')


class PridatKnihu(generic.edit.CreateView):
    form_class = KnihaForm
    template_name = 'Librapp/pridat_knihu.html'
    form_search = VyhledavaniISBNForm
    form_book = KnihaForm
    api_key = 'AIzaSyC93CTzl4KyuzwzGomQ2kipnPcj-0ZuubU'

    def get(self, request):
        form = self.form_search(None)
        book_form = self.form_book(None)
        return render(request, self.template_name, {'form': form, 'book_form': book_form})

    def post(self, request):

        search_form = self.form_search(request.POST)
        book_form_empty: KnihaForm = self.form_book(None)

        if request.POST['action'] == 'Vyhledej knihu':

            if search_form.is_valid():
                isbn = search_form.cleaned_data['isbn']
                book_data = self.get_book_data(isbn)

                if book_data:
                    initial_data = {
                        'nazev': book_data.get('title', ''),
                        'podtitul': book_data.get('subtitle', ''),
                        'autor': ', '.join(book_data.get('authors', [])),
                        'rok_vydani': book_data.get('publishedDate', ''),
                        'jazyk': book_data.get('language', ''),
                        'ISBN10': book_data.get("industryIdentifiers")[0]['identifier'],
                        'ISBN13': book_data.get("industryIdentifiers")[1]['identifier'],
                        'majitel': request.user
                    }

                    book_form = KnihaForm(initial=initial_data)
                    return render(request, f'Librapp/pridat_knihu.html',
                                  {'form': search_form, 'book_form': book_form})
                else:
                    search_form.add_error('isbn', 'ISBN nenalezeno')
                    return render(request, f'Librapp/pridat_knihu.html',
                                  {'form': search_form, 'book_form': book_form_empty})

        elif request.POST['action'] == 'Ulož knihu':
            book_form = self.form_book(request.POST)

            if book_form.is_valid():
                book_form.save(commit=True)
                return render(request, self.template_name, {'form': search_form, 'book_form': book_form_empty})
            else:
                search_form.add_error('isbn', 'ISBN nenalezeno')
                return render(request, self.template_name, {'form': search_form, 'book_form': book_form_empty})
        else:
            return HttpResponse("něco se posralo")

    def get_book_data(self, isbn):
        google_books_api_url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={self.api_key}'
        response = requests.get(google_books_api_url)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                book_info = data['items'][0]['volumeInfo']
                return book_info
        return None


class UzivatelViewLogin(generic.edit.CreateView):
    form_class = LoginForm
    template_name = "LibrApp/login.html"

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect('index')
        return render(request, self.template_name, {'form': form})


class UzivatelViewRegister(generic.edit.CreateView):
    form_class = RegistraceForm
    model = Uzivatel
    template_name = 'Librapp/registrace.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            uzivatel = form.save(commit=False)
            password = form.cleaned_data['password']
            uzivatel.set_password(password)
            uzivatel.save()
            login(request, uzivatel)
            return redirect("index")

        return render(request, self.template_name, {"form": form})


def logout_uzivatel(request):
    logout(request)
    return redirect('index')


class KnihyUzivatele(LoginRequiredMixin, generic.ListView):
    template_name = "Librapp/uzivatel_knihy.html"
    context_object_name = "knihy"

    def get_queryset(self):
        # Get the logged-in user
        user = self.request.user

        query = self.request.GET.get('q')
        if query:
            return Kniha.objects.filter(
                Q(nazev__icontains=query) |
                Q(autor__icontains=query),
                majitel=user
            ).order_by('-id')
        else:
            return Kniha.objects.filter(majitel=user).order_by('-id')


class Profil(LoginRequiredMixin, generic.TemplateView):
    template_name = 'Librapp/profil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('pk')
        query = self.request.GET.get('q')
        user = Uzivatel.objects.get(id=user_id)
        context['user'] = user

        if query:

            context['knihy'] = Kniha.objects.filter(
                Q(nazev__icontains=query) |
                Q(autor__icontains=query),
                majitel=user
            ).order_by('-id')
        else:
            context['knihy'] = Kniha.objects.filter(majitel=user).order_by('-id')

        return context


class SeznamUzivatelu(generic.ListView):
    template_name = "Librapp/uzivatele.html"
    context_object_name = "uzivatele"

    def get_queryset(self):

        query = self.request.GET.get('q')
        if query:
            return Uzivatel.objects.filter(
                Q(jmeno__icontains=query) |
                Q(prijmeni__icontains=query) |
                Q(uzivatelske_jmeno__icontains=query)
            ).order_by('-id')
        else:
            return Uzivatel.objects.all().order_by('-id')
