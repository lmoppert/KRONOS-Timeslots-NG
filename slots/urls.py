from django.urls import path
from slots import views

urlpatterns = [
    path('', views.index, name='index'),
]
