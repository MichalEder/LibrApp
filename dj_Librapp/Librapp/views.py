from django.shortcuts import render, HttpResponse
from django.views import generic
from .models import Kniha
from django.db.models import Q
from .forms import KnihaForm, VyhledavaniISBNForm
import requests

# Create your views here.
class Detail(generic.DetailView):

    model = Kniha
    template_name = 'Librapp/detail.html'


class SeznamKnih(generic.ListView):

    template_name = "Librapp/index.html"
    context_object_name = "knihy"


    def get_queryset(self):

        query = self.request.GET.get('q')
        if query:
            # If a search query is provided, filter books based on title using a case-insensitive search
            return Kniha.objects.filter(
                Q(nazev__icontains=query) |
                Q(autor__icontains=query) |
                Q(majitel__icontains=query)
            ).order_by('-id')
        else:
            return Kniha.objects.all().order_by('-id')

class PridatKnihu(generic.edit.CreateView):
    form_class = KnihaForm
    template_name = 'Librapp/pridat_knihu.html'
    form_search = VyhledavaniISBNForm
    form_book = KnihaForm

    def get(self, request):
        form = self.form_search(None)
        book_form = self.form_book(None)
        return render(request, self.template_name, {'form': form, 'book_form': book_form})

    def post(self, request):

        search_form = self.form_search(request.POST)

        if request.POST['action'] == 'Vyhledej knihu':

            if search_form.is_valid():
                isbn = search_form.cleaned_data['isbn']
                book_data = self.get_book_data(isbn)

                if book_data:
                    initial_data = {
                        'nazev': book_data.get('title', ''),
                        'autor': ', '.join(book_data.get('authors', [])),
                        'rok_vydani': book_data.get('publishedDate', ''),
                        'jazyk': book_data.get('language', ''),
                        'ISBN10': book_data.get("industryIdentifiers")[0]['identifier'],
                        'ISBN13': book_data.get("industryIdentifiers")[1]['identifier']
                    }

                    book_form = KnihaForm(initial=initial_data)
                    return render(request, f'Librapp/pridat_knihu.html', {'form': search_form, 'book_form': book_form})
                else:
                    search_form.add_error('isbn', 'ISBN nenalezeno')
                    return render(request, f'Librapp/pridat_knihu.html', {'form': search_form})
        elif request.POST['action'] == 'Ulož knihu':
            book_form = self.form_book(request.POST)
            if book_form.is_valid():
                book_form.save(commit=True)
                return render(request, self.template_name, {'form': search_form, 'book_form': book_form})
            else:
                return render(request, self.template_name, {'form': search_form, 'book_form': book_form})
        else:
            return HttpResponse("něco se posralo")

    def get_book_data(self, isbn):
        google_books_api_url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}'
        response = requests.get(google_books_api_url)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                book_info = data['items'][0]['volumeInfo']
                return book_info
        return None