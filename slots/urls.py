from django.contrib.auth import views as auth_views
from django.urls import path
from slots import views


datematch = '/date/<int:year>/<int:month>/<int:day>'
urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('<int:pk>', views.StationRedirect.as_view(), name='station'),
    path('docks/<int:pk>'+datematch,
         views.StationDocks.as_view(), name='stationdocks'),
    path('slot/<int:station>/<int:dock>/<int:line>'+datematch,
         views.DockSlot.as_view(), name='dockslot'),
    # path('silos/<int:pk>/date/<int:year>/<int:month>/<int:day>',
    #      views.StationSilos.as_view(), name='stationsilos'),
]
