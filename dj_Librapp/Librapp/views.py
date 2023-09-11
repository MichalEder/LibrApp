from django.shortcuts import render
from django.views import generic
from .models import Kniha
from django.db.models import Q
from .forms import KnihaForm

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
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(owner__icontains=query)
            ).order_by('-id')
        else:
            return Kniha.objects.all().order_by('-id')

class PridatKnihu(generic.edit.CreateView):
    form_class = KnihaForm
    template_name = 'Librapp/pridat_knihu.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(commit=True)
        return render(request, self.template_name, {"form": form})