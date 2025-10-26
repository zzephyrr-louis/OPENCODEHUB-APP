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
    
    # Password Reset with Security Question
    path('password-reset/', views.password_reset_security, name='password_reset'),
    
    # Project-related URLs
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/my/', views.my_projects, name='my_projects'),
    path('projects/browse/', views.browse_projects, name='browse_projects'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/upload/', views.upload_file, name='upload_file'),
    
    # Upload folder and create document
    path('upload-folder/', views.upload_folder, name='upload_folder'),
    path('document/create/', views.create_document, name='create_document'),

    # Browse Projects
    path('browse/', views.browse_projects, name='browse_projects'),
    
    # Shared with me
    path('shared/', views.shared_with_me, name='shared_with_me'),
    
    # Share/Unshare
    path('project/<int:project_id>/share/', views.share_project, name='share_project'),
    path('project/<int:project_id>/unshare/<int:user_id>/', views.unshare_project, name='unshare_project'),
    
    # Shareable Link
    path('project/<int:project_id>/generate-link/', views.generate_share_link, name='generate_share_link'),
    path('share/<uuid:share_uuid>/', views.view_shared_project, name='view_shared_project'),

    # Version History
    path('projects/<int:project_id>/versions/', views.version_history, name='version_history'),
    path('projects/<int:project_id>/versions/<int:version_id>/', views.view_version, name='view_version'),
    path('projects/<int:project_id>/versions/<int:version_id>/restore/', views.restore_version, name='restore_version'),
]
