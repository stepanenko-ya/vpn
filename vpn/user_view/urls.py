from django.urls import path
from . import views
from .views import *


urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('profile/', UserProfile.as_view(), name='profile'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('add_site/', AddSite.as_view(), name='site_creation'),
    path('site_list/', SitesList.as_view(), name='sites_list'),
    path('<str:site_name>/<path:url_path>/', views.test, name=''),

]

