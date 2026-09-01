from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from .forms import AddVehicleForm, AdminSignUpForm, SignUpForm
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
@login_required
def add_vehicle(request):
    """Lets an existing (non-admin) user register an additional vehicle."""
    if request.method == 'POST':
        form = AddVehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            vehicle.save()
            messages.success(request, f'Vehicle {vehicle.plate_number} added to your account.')
            return redirect(reverse('dashboard:home'))
    else:
        form = AddVehicleForm()
    return render(request, 'accounts/add_vehicle.html', {'form': form})