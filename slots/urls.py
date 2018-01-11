from django.urls import path
from slots import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>', views.StationDetail.as_view(), name='station'),
    path('<int:pk>/date/<int:year>/<int:month>/<int:day>',
         views.StationDetail.as_view(), name='stationdate'),
]
