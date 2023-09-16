from django.urls import path
from . import views

urlpatterns = [

    path('index', views.SeznamKnih.as_view(), name='index'),
    path('pridat_knihu', views.PridaniKnihy.as_view(), name='pridat knihu'),
    path('<int:pk>/detail', views.DetailKnihy.as_view(), name='detail'),
    path('<int:pk>/uprav_knihu', views.UpraveniKnihy.as_view(), name='edit'),
    path('<int:pk>/odstran_knihu', views.OdstraneniKnihy.as_view(), name='delete'),
    path('registrace', views.UzivatelRegisterace.as_view(), name='registrace'),
    path('login', views.UzivatelLogin.as_view(), name='login'),
    path('logout', views.logout_uzivatel, name='logout'),
    path('uzivatele', views.SeznamUzivatelu.as_view(), name='uzivatele'),
    path('<int:pk>/odstran_uzivatele', views.OdstraneniUzivatele.as_view(), name='odstran_uzivatele'),
    path('<int:pk>/profil', views.DetailUzivatele.as_view(), name='profil'),
    path('<int:pk>/uprav_profil', views.UpraveniUzivatele.as_view(), name='uprav_profil')


]