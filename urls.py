from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing),
    path('login/', views.login),
    path('register/', views.register),

    path('load-add-location/', views.loadAddLocation),
    path('add-location/<str:id>', views.addLocation),

    path('search/', views.search),

    path('load-contributions/', views.loadContributions),
    path('contributions/<str:id>', views.contributions),

    path('city/<str:id>', views.city),

    path('load-location/<str:id>', views.loadLocation),
    path('location/<str:locId>/<str:userId>', views.location),
]
