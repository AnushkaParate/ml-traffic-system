from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import AdminSignUpForm, SignUpForm


class UserSignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('dashboard:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class AdminSignUpView(CreateView):
    form_class = AdminSignUpForm
    template_name = 'accounts/admin_signup.html'
    success_url = reverse_lazy('dashboard:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class TrafficLoginView(LoginView):
    template_name = 'accounts/login.html'


class TrafficLogoutView(LogoutView):
    pass
