from django.contrib.auth import views as auth_views
from django.urls import path
from slots import views


date_match = '/date/<int:year>/<int:month>/<int:day>'
urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('<int:pk>', views.StationRedirect.as_view(), name='station'),
    path('docks/<int:pk>' + date_match,
         views.StationDocks.as_view(), name='stationdocks'),
    path('slot/<int:dock>/<int:index>/<int:line>' + date_match,
         views.SlotRedirect.as_view(), name='getslot'),
    path('slot/<int:pk>', views.SlotDetail.as_view(), name='slotdetail'),
    path('newslot/<int:pk>', views.SlotDetail.as_view(), name='newslot'),
    # path('silos/<int:pk>/date/<int:year>/<int:month>/<int:day>',
    #      views.StationSilos.as_view(), name='stationsilos'),
]
