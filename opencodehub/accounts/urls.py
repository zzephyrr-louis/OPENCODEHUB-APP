from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Landing page
    path('', views.landing, name='landing'),
    
    # Authentication URLs
    path('register/', views.CustomRegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('home/', views.home, name='home'),
    
    # Password Reset URLs
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/login/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Project-related URLs
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/my/', views.my_projects, name='my_projects'),
    path('projects/browse/', views.browse_projects, name='browse_projects'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/upload/', views.upload_file, name='upload_file'),
    
    # Browse Projects
    path('browse/', views.browse_projects, name='browse_projects'),
    
    # Shared with me
    path('shared/', views.shared_with_me, name='shared_with_me'),
    
    # Share/Unshare
    path('project/<int:project_id>/share/', views.share_project, name='share_project'),
    path('project/<int:project_id>/unshare/<int:user_id>/', views.unshare_project, name='unshare_project'),
]
