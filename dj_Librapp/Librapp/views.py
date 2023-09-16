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


class UpraveniKnihy(generic.UpdateView):
    """
    View pro úpravu knihy.

    Attributes:
        model (Type[Kniha]): Model knihy, který bude použit pro tuto view.
        form (Type[KnihaForm]): Formulář pro úpravu knihy.
        template_name (str): Název šablony pro zobrazení úpravy knihy.
        fields (list[str]): Pole polí, která budou zobrazena ve formuláři pro úpravu knihy.
    """

    model = Kniha
    form = KnihaForm
    template_name = 'Librapp/uprav_knihu.html'
    fields = ['nazev', 'autor', 'rok_vydani', 'zanr', 'jazyk', 'ISBN10', 'ISBN13', 'majitel']

    def get_success_url(self):
        """
        Získá URL pro přesměrování po úspěšné aktualizaci knihy.

        Returns:
            str: URL pro přesměrování na detail knihy po aktualizaci.
        """
        return reverse_lazy('detail', kwargs={'pk': self.object.id})



class UpraveniUzivatele(generic.UpdateView):
    """
    View pro úpravu uživatele.

    Attributes:
        model (Type[Uzivatel]): Model uživatele, který bude použit pro tuto view.
        form (Type[RegistraceForm]): Formulář pro úpravu uživatelského profilu.
        template_name (str): Název šablony pro zobrazení úpravy profilu.
        fields (list[str]): Pole polí, která budou zobrazena ve formuláři pro úpravu.
    """
    model = Uzivatel
    form = RegistraceForm
    template_name = 'Librapp/uprav_profil.html'
    fields = ['email', 'jmeno', 'prijmeni', 'uzivatelske_jmeno']

    def get_success_url(self):
        """Získá URL pro přesměrování po úspěšné aktualizaci uživatelského profilu."""
        return reverse_lazy('profil', kwargs={'pk': self.object.id})


class OdstraneniKnihy(generic.DeleteView):
    """
    View pro odstranění knihy.

    Attributes:
        model (Type[Kniha]): Model knihy, který bude použit pro tuto view.
        template_name (str): Název šablony pro zobrazení odstranění knihy.
    """
    model = Kniha
    template_name = 'Librapp/odstran_knihu.html'

    def get_context_data(self, **kwargs):
        """
        Získá a rozšíří kontext pro zobrazení šablony.

        Args:
            **kwargs: Klíčové argumenty předávané nadtřídě.
        """
        context = super().get_context_data(**kwargs)
        context['confirmation_message'] = f"Opravdu si přejete smazat knihu {self.object.nazev}? "
        return context

    def get_success_url(self) -> str:
        """
        Získá URL pro přesměrování po úspěšném smazání knihy.

        Returns:
            str: URL pro přesměrování na uživatelský profil po smazání knihy.
        """
        user_id = self.request.user.id
        return reverse_lazy('profil', kwargs={'pk': user_id})


class OdstraneniUzivatele(generic.DeleteView):
    """
    View pro odstranění uživatele.

    Attributes:
        model (Type[Uzivatel]): Model uživatele, který bude použit pro tuto view.
        template_name (str): Název šablony pro zobrazení odstranění uživatele.
        success_url (str): URL pro přesměrování po úspěšném smazání uživatele.
    """
    model = Uzivatel
    template_name = 'Librapp/odstran_uzivatele.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        """
        Získá a rozšíří kontext pro zobrazení šablony.

        Args:
            **kwargs: Klíčové argumenty předávané nadtřídě.
        """
        context = super().get_context_data(**kwargs)
        context[
            'confirmation_message'] = f"Opravdu si přejete smazat účet uživatele {self.object.jmeno} {self.object.prijmeni}?"
        return context


class DetailKnihy(generic.DetailView):
    """
    View pro zobrazení detailu knihy.

    Attributes:
        model (Type[Kniha]): Model knihy, který bude použit pro tuto view.
        template_name (str): Název šablony pro zobrazení detailu knihy.
    """
    model = Kniha
    template_name = 'Librapp/detail.html'


class SeznamKnih(generic.ListView):
    """
    View pro zobrazení seznamu knih.

    Attributes:
        template_name (str): Název šablony pro zobrazení seznamu knih.
        context_object_name (str): Název objektu v kontextu, který obsahuje seznam knih.
    """
    template_name = "Librapp/index.html"
    context_object_name = "knihy"

    def get_queryset(self):
        """
        Získá seznam knih k zobrazení na základě vyhledávacího dotazu.

        Returns:
            QuerySet[Kniha]: Queryset obsahující seznam knih pro zobrazení.
        """
        query = self.request.GET.get('q')
        if query:
            return Kniha.objects.filter(
                Q(nazev__icontains=query) |
                Q(autor__icontains=query) |
                Q(podtitul__icontains=query)
            ).order_by('-id')
        else:
            return Kniha.objects.all().order_by('-id')


class VyhledavaniISBN:
    """
    Třída pro vyhledávání knihy podle ISBN pomocí Google Books API.

    Attributes:
        api_key (str): Klíč pro přístup k Google Books API (TODO: skryt apikey).
        isbn (str): ISBN knihy, podle které je vyhledáváno.
    """
    def __init__(self, isbn: str):
        self.api_key = 'AIzaSyC93CTzl4KyuzwzGomQ2kipnPcj-0ZuubU' #TODO: skryt apikey
        self.isbn = isbn

    def get_book_data(self):
        """
        Získejte data o knize z Google Books API na základě ISBN.

        Returns:
            dict or None: Data o knize z Google Books API nebo None, pokud kniha nebyla nalezena.
        """
        google_books_api_url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{self.isbn}&key={self.api_key}'
        response = requests.get(google_books_api_url)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                book_info = data['items'][0]['volumeInfo']
                return book_info
        return None


class PridaniKnihy(generic.edit.CreateView):
    """
    View pro přidání knihy.

    Attributes:
        form_class (Type[KnihaForm]): Třída formuláře pro přidání knihy.
        template_name (str): Název šablony pro zobrazení formuláře.
        form_search (Type[VyhledavaniISBNForm]): Třída formuláře pro vyhledávání knihy podle ISBN.
        form_book (Type[KnihaForm]): Třída formuláře pro přidání knihy.
    """
    form_class = KnihaForm
    template_name = 'Librapp/pridat_knihu.html'
    form_search = VyhledavaniISBNForm
    form_book = KnihaForm

    def get(self, request):
        """
        Získá GET požadavek pro zobrazení formuláře pro přidání knihy.

        Args:
            request (HttpRequest): HTTP GET požadavek.

        Returns:
            HttpResponse: Odpověď s vykresleným formulářem.
        """
        form = self.form_search(None)
        book_form = self.form_book(None)
        return render(request, self.template_name, {'form': form, 'book_form': book_form})

    def post(self, request):
        """
        Získá POST požadavek a zpracuje přidání knihy nebo vyhledání knihy podle ISBN.

        Args:
            request (HttpRequest): HTTP POST požadavek.

        Returns:
            HttpResponse: Odpověď po zpracování požadavku.
        """
        search_form = self.form_search(request.POST)
        book_form_empty: KnihaForm = self.form_book(None)

        if request.POST['action'] == 'Vyhledej knihu':

            if search_form.is_valid():
                vyhledavani = VyhledavaniISBN(search_form.cleaned_data['isbn'])
                book_data = vyhledavani.get_book_data()

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
                search_form.add_error('isbn', 'Kniha neuložena')
                return render(request, self.template_name, {'form': search_form, 'book_form': book_form_empty})
        else:
            return HttpResponse("Něco se po...kazilo")


class UzivatelLogin(generic.edit.CreateView):
    """
    View pro přihlášení uživatele.

    Attributes:
        form_class (Type[LoginForm]): Třída formuláře pro přihlášení.
        template_name (str): Název šablony pro zobrazení přihlašovacího formuláře.
    """
    form_class = LoginForm
    template_name = "LibrApp/login.html"

    def get(self, request):
        """
        Získá GET požadavek pro zobrazení přihlašovacího formuláře.

        Args:
            request (HttpRequest): HTTP GET požadavek.

        Returns:
            HttpResponse: Odpověď s vykresleným přihlašovacím formulářem.
        """
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """
        Získá POST požadavek a zpracuje přihlášení uživatele.

        Args:
            request (HttpRequest): HTTP POST požadavek.

        Returns:
            HttpResponse: Odpověď po zpracování přihlašovacího požadavku.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect('index')
        return render(request, self.template_name, {'form': form})


class UzivatelRegistrace(generic.edit.CreateView):
    """
    View pro registraci uživatele.

    Attributes:
        form_class (Type[RegistraceForm]): Třída formuláře pro registraci uživatele.
        model (Type[Uzivatel]): Model uživatele, který bude použit pro tuto view.
        template_name (str): Název šablony pro zobrazení registračního formuláře.
    """
    form_class = RegistraceForm
    model = Uzivatel
    template_name = 'Librapp/registrace.html'

    def get(self, request):
        """
        Získá GET požadavek pro zobrazení registračního formuláře.

        Args:
            request (HttpRequest): HTTP GET požadavek.

        Returns:
            HttpResponse: Odpověď s vykresleným registračním formulářem.
        """
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Získá POST požadavek a zpracuje registraci uživatele.

        Args:
            request (HttpRequest): HTTP POST požadavek.

        Returns:
            HttpResponse: Odpověď po zpracování registračního požadavku.
        """
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
    """
    View pro odhlášení uživatele.

    Args:
        request (HttpRequest): HTTP požadavek.

    Returns:
        HttpResponseRedirect: Přesměrování uživatele na stránku 'index' po odhlášení.
    """
    logout(request)
    return redirect('index')


class DetailUzivatele(LoginRequiredMixin, generic.TemplateView):
    """
    View pro zobrazení detailu uživatele.

    Attributes:
        template_name (str): Název šablony pro zobrazení detailu uživatele.
    """
    template_name = 'Librapp/profil.html'

    def get_context_data(self, **kwargs):
        """
        Získá a rozšíří kontext pro zobrazení šablony.

        Args:
            **kwargs: Klíčové argumenty předávané nadtřídě.

        Returns:
            dict: Rozšířený kontext obsahující informace o uživateli a jeho knihách.
        """
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('pk')
        query = self.request.GET.get('q')
        user = Uzivatel.objects.get(id=user_id)
        context['user'] = user

        if query:
            context['knihy'] = Kniha.objects.filter(
                Q(nazev__icontains=query) |
                Q(podtitul__icontains=query) |
                Q(autor__icontains=query),
                majitel=user
            ).order_by('-id')

        else:
            context['knihy'] = Kniha.objects.filter(majitel=user).order_by('-id')

        return context


class SeznamUzivatelu(generic.ListView):
    """
    View pro zobrazení seznamu uživatelů.

    Attributes:
        template_name (str): Název šablony pro zobrazení seznamu uživatelů.
        context_object_name (str): Název proměnné v kontextu, do které bude uložen seznam uživatelů.
    """
    template_name = "Librapp/uzivatele.html"
    context_object_name = "uzivatele"

    def get_queryset(self):
        """
         Získá seznam uživatelů k zobrazení na základě vyhledávacího dotazu.

         Returns:
             QuerySet[Uzivatel]: Queryset obsahující seznam uživatelů pro zobrazení.
         """
        query = self.request.GET.get('q')
        if query:
            return Uzivatel.objects.filter(
                Q(jmeno__icontains=query) |
                Q(prijmeni__icontains=query) |
                Q(uzivatelske_jmeno__icontains=query)
            ).order_by('-id')
        else:
            return Uzivatel.objects.all().order_by('-id')
