from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('calculator/', views.calculator, name='calculator'),
    path('spot/add/', views.spot_add, name='spot_add'),
    path('trip/add/', views.trip_add, name='trip_add'),
]