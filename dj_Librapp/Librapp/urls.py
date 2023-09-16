from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.SeznamKnih.as_view(), name='index'),  # Seznam knih
    path('pridat_knihu/', views.PridaniKnihy.as_view(), name='pridat_knihu'),  # Přidat knihu
    path('<int:pk>/detail/', views.DetailKnihy.as_view(), name='detail'),  # Detail knihy
    path('<int:pk>/uprav_knihu/', views.UpraveniKnihy.as_view(), name='edit'),  # Úprava knihy
    path('<int:pk>/odstran_knihu/', views.OdstraneniKnihy.as_view(), name='delete'),  # Odstranit knihu
    path('registrace/', views.UzivatelRegistrace.as_view(), name='registrace'),  # Registrace uživatele
    path('login/', views.UzivatelLogin.as_view(), name='login'),  # Přihlášení uživatele
    path('logout/', views.logout_uzivatel, name='logout'),  # Odhlášení uživatele
    path('uzivatele/', views.SeznamUzivatelu.as_view(), name='uzivatele'),  # Seznam uživatelů
    path('<int:pk>/odstran_uzivatele/', views.OdstraneniUzivatele.as_view(), name='odstran_uzivatele'),  # Odstranit uživatele
    path('<int:pk>/profil/', views.DetailUzivatele.as_view(), name='profil'),  # Detail uživatele
    path('<int:pk>/uprav_profil/', views.UpraveniUzivatele.as_view(), name='uprav_profil'),  # Úprava profilu uživatele
]