from django.contrib import admin
from .models import Kniha, Zanr, Uzivatel
# Register your models here.
admin.site.register(Kniha)
admin.site.register(Zanr)
admin.site.register(Uzivatel)