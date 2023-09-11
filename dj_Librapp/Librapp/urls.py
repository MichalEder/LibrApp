from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/detail', views.Detail.as_view(), name='detail'),
    path('index', views.SeznamKnih.as_view(), name='seznam'),
    path('pridat_knihu', views.PridatKnihu.as_view(), name='pridat knihu')
]