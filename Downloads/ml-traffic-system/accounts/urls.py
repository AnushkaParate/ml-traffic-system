from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.UserSignUpView.as_view(), name='signup'),
    path('signup/admin/', views.AdminSignUpView.as_view(), name='admin_signup'),
    path('login/', views.TrafficLoginView.as_view(), name='login'),
    path('logout/', views.TrafficLogoutView.as_view(), name='logout'),
]
