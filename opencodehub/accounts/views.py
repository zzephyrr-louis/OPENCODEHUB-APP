from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, CustomLoginForm, CustomPasswordResetForm
from .models import Project, ProjectFile, Comment
from django.shortcuts import get_object_or_404
import os


def landing(request):
    """Landing page view"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'accounts/landing.html')

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
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class CustomLoginView(LoginView):
    """Login view"""
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid credentials. Please try again.')
        return super().form_invalid(form)

@login_required
def home(request):
    """Home/Dashboard page view"""
    # Get user's projects
    projects = Project.objects.filter(owner=request.user).order_by('-updated_at')
    
    # Get recent activities (last 5 projects updated)
    recent_activities = []
    for project in projects[:5]:
        recent_activities.append({
            'time': f"{project.updated_at.strftime('%H:%M %p')}",
            'project_name': project.title,
            'description': f'Updated {project.updated_at.strftime("%B %d, %Y")}'
        })
    
    context = {
        'projects': projects,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'accounts/home.html', context)

def custom_logout(request):
    """Custom logout view"""
    user_name = request.user.first_name if request.user.is_authenticated else None
    logout(request)
    if user_name:
        messages.success(request, f'Goodbye, {user_name}! You have been logged out successfully.')
    return redirect('landing')

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
    

    

@login_required
def create_project(request):
    """Create new project"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        is_public = request.POST.get('is_public') == 'on'
        
        project = Project.objects.create(
            title=title,
            description=description,
            owner=request.user,
            is_public=is_public
        )
        messages.success(request, f'Project "{title}" created successfully!')
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'accounts/create_project.html')

@login_required
def project_detail(request, project_id):
    """View project details"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check permissions
    if not project.is_public and project.owner != request.user:
        messages.error(request, 'You do not have permission to view this project.')
        return redirect('dashboard')
    
    files = project.files.all()
    comments = project.comments.all()
    versions = project.versions.all()[:5]  # Latest 5 versions
    
    return render(request, 'accounts/project_detail.html', {
        'project': project,
        'files': files,
        'comments': comments,
        'versions': versions
    })

@login_required
def upload_file(request, project_id):
    """Upload file to project"""
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        
        for file in files:
            file_type = file.name.split('.')[-1] if '.' in file.name else 'unknown'
            
            ProjectFile.objects.create(
                project=project,
                name=file.name,
                file=file,
                file_type=file_type,
                size=file.size
            )
        
        messages.success(request, f'{len(files)} file(s) uploaded successfully!')
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'accounts/upload_file.html', {'project': project})

@login_required
def my_projects(request):
    """List user's projects"""
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'accounts/my_projects.html', {'projects': projects})

@login_required
def browse_projects(request):
    """Browse public projects"""
    projects = Project.objects.filter(is_public=True).order_by('-created_at')
    return render(request, 'accounts/browse_projects.html', {'projects': projects})