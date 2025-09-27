from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, CustomLoginForm, CustomPasswordResetForm

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')

class CustomRegisterView(CreateView):
    """Registration view"""
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! You can now log in.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

class CustomLoginView(LoginView):
    """Login view"""
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid credentials. Please try again.')
        return super().form_invalid(form)

@login_required
def dashboard(request):
    """Dashboard view for authenticated users"""
    return render(request, 'accounts/dashboard.html', {
        'user': request.user
    })

def custom_logout(request):
    """Custom logout view"""
    user_name = request.user.first_name if request.user.is_authenticated else None
    logout(request)
    if user_name:
        messages.success(request, f'Goodbye, {user_name}! You have been logged out successfully.')
    return redirect('home')

class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view"""
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'

    def form_valid(self, form):
        messages.success(self.request, 'Password reset email has been sent to your email address.')
        return super().form_valid(form)