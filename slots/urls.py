from django.urls import path
from slots import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>', views.StationRedirect.as_view(), name='station'),
    path('docks/<int:pk>/date/<int:year>/<int:month>/<int:day>',
         views.StationDocks.as_view(), name='stationdocks'),
    # path('silos/<int:pk>/date/<int:year>/<int:month>/<int:day>',
    #      views.StationSilos.as_view(), name='stationsilos'),
]
