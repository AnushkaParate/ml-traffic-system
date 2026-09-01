from django.urls import path

from . import views

app_name = 'signal_control'

urlpatterns = [
    path('simulator/', views.signal_simulator, name='simulator'),
]