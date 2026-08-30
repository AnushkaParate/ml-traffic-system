from django.urls import path

from . import views

app_name = 'challan'

urlpatterns = [
    path('report/', views.report_violation, name='report_violation'),
    path('<int:challan_id>/pdf/', views.download_challan_pdf, name='download_pdf'),
    path('<int:challan_id>/pay/', views.mark_as_paid, name='mark_as_paid'),
    path('all/', views.all_challans, name='all_challans'),
]