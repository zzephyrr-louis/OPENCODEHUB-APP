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
from django.db.models import Q
from accounts.models import User
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
    logout(request)
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
    
    # Check permissions - allow owner, shared users, or public projects
    if not project.is_public and project.owner != request.user and request.user not in project.shared_with.all():
        messages.error(request, 'You do not have permission to view this project.')
        return redirect('home')
    
    # UPDATED: Handle comment posting
    if request.method == 'POST':
        comment_text = request.POST.get('text')
        if comment_text:
            Comment.objects.create(
                project=project,
                author=request.user,
                content=comment_text
            )
            messages.success(request, 'Comment added successfully!')
            return redirect('project_detail', project_id=project.id)
    
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
    # Allow owner and shared users to upload files
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user is owner or has access
    if project.owner != request.user and request.user not in project.shared_with.all():
        messages.error(request, 'You do not have permission to upload files to this project.')
        return redirect('project_detail', project_id=project.id)
    
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

# BROWSE PROJECTS 
@login_required
def browse_projects(request):
    """Browse all public projects with search and filter"""
    
    # Get search query from URL parameters
    search_query = request.GET.get('search', '')
    
    # Start with all public projects, excluding user's own projects
    projects = Project.objects.filter(is_public=True).exclude(owner=request.user).order_by('-updated_at')
    
    # Apply search filter if query exists
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(owner__first_name__icontains=search_query) |
            Q(owner__last_name__icontains=search_query) |
            Q(owner__username__icontains=search_query)
        )
    
    context = {
        'projects': projects,
        'search_query': search_query,
        'total_count': projects.count()
    }
    
    return render(request, 'accounts/browse_projects.html', context)

# SHARED WITH ME 
@login_required
def shared_with_me(request):
    """View projects shared with the current user"""
    
    # Get all projects where current user is in shared_with
    shared_projects = Project.objects.filter(
        shared_with=request.user
    ).order_by('-updated_at')
    
    context = {
        'projects': shared_projects,
        'total_count': shared_projects.count()
    }
    
    return render(request, 'accounts/shared_with_me.html', context)

# SHARE PROJECT 
@login_required
def share_project(request, project_id):
    """Share a project with other users"""
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if request.method == 'POST':
        # Get username or email to share with
        share_with = request.POST.get('share_with', '').strip()
        
        if not share_with:
            messages.error(request, 'Please enter a username or email.')
            return redirect('project_detail', project_id=project.id)
        
        try:
            # Find user by username or email
            user_to_share = User.objects.get(
                Q(username=share_with) | Q(email=share_with)
            )
            
            # Don't allow sharing with yourself
            if user_to_share == request.user:
                messages.error(request, 'You cannot share a project with yourself!')
                return redirect('project_detail', project_id=project.id)
            
            # Check if already shared
            if user_to_share in project.shared_with.all():
                messages.warning(request, f'Project is already shared with {user_to_share.username}!')
            else:
                # Add user to shared_with
                project.shared_with.add(user_to_share)
                messages.success(request, f'Project shared with {user_to_share.username}!')
            
        except User.DoesNotExist:
            messages.error(request, f'User "{share_with}" not found!')
    
    return redirect('project_detail', project_id=project.id)


# UNSHARE PROJECT
@login_required
def unshare_project(request, project_id, user_id):
    """Remove a user from project sharing"""
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    user_to_remove = get_object_or_404(User, id=user_id)
    
    # Remove user from shared_with
    project.shared_with.remove(user_to_remove)
    messages.success(request, f'Removed {user_to_remove.username} from project!')
    
    return redirect('project_detail', project_id=project.id)

# SECURITY QUESTION PASSWORD RESET
def password_reset_security(request):
    """Password reset using security question"""
    if request.method == 'POST':
        step = request.POST.get('step', '1')
        
        if step == '1':
            # Step 1: Verify username and show security question
            username = request.POST.get('username', '').strip()
            
            try:
                user = User.objects.get(username=username)
                
                if not user.security_question:
                    messages.error(request, 'This account does not have a security question set up.')
                    return redirect('password_reset')
                
                # Get the question text
                questions_dict = {
                    'pet': "What is your first pet's name?",
                    'city': "In what city were you born?",
                    'school': "What is your elementary school name?",
                    'color': "What is your favorite color?",
                    'food': "What is your favorite food?",
                }
                security_question = questions_dict.get(user.security_question, user.security_question)
                
                return render(request, 'accounts/password_reset_security.html', {
                    'step': 2,
                    'username': username,
                    'security_question': security_question
                })
                
            except User.DoesNotExist:
                messages.error(request, 'Username not found.')
                return render(request, 'accounts/password_reset_security.html', {'step': 1})
        
        elif step == '2':
            # Step 2: Verify answer and reset password
            username = request.POST.get('username')
            security_answer = request.POST.get('security_answer', '').lower().strip()
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            try:
                user = User.objects.get(username=username)
                
                if user.security_answer.lower().strip() == security_answer:
                    if new_password == confirm_password:
                        if len(new_password) >= 8:
                            user.set_password(new_password)
                            user.save()
                            messages.success(request, 'Password reset successful! You can now login with your new password.')
                            return redirect('login')
                        else:
                            messages.error(request, 'Password must be at least 8 characters long.')
                    else:
                        messages.error(request, 'Passwords do not match.')
                else:
                    messages.error(request, 'Incorrect answer to security question.')
                
                # Return to step 2 with error
                questions_dict = {
                    'pet': "What is your first pet's name?",
                    'city': "In what city were you born?",
                    'school': "What is your elementary school name?",
                    'color': "What is your favorite color?",
                    'food': "What is your favorite food?",
                }
                security_question = questions_dict.get(user.security_question, user.security_question)
                
                return render(request, 'accounts/password_reset_security.html', {
                    'step': 2,
                    'username': username,
                    'security_question': security_question
                })
                
            except User.DoesNotExist:
                messages.error(request, 'An error occurred. Please try again.')
                return redirect('password_reset')
    
    # GET request - show step 1
    return render(request, 'accounts/password_reset_security.html', {'step': 1})