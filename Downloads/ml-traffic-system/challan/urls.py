from django.urls import path

from . import views

app_name = 'challan'

urlpatterns = [
    path('report/', views.report_violation, name='report_violation'),
]