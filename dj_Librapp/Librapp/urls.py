from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='index'),
    path('<int:pk>/detail', views.Detail.as_view(), name='detail'),
    path('/index', views.SeznamKnih.as_view(), name='seznam')


]