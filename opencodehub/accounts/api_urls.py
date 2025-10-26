from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ProjectViewSet,
    ProjectVersionViewSet,
    ProjectVersionListView,
    LatestVersionView
)

# Create a router for viewsets
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='api-project')

# API URL patterns
api_urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Project version endpoints
    path('projects/<int:project_id>/versions/', 
         ProjectVersionListView.as_view(), 
         name='api-project-versions-list'),
    
    path('projects/<int:project_id>/versions/upload/', 
         ProjectVersionViewSet.as_view({'post': 'create'}), 
         name='api-project-version-upload'),
    
    path('projects/<int:project_id>/versions/latest/', 
         LatestVersionView.as_view(), 
         name='api-project-latest-version'),
    
    path('projects/<int:project_id>/versions/<int:pk>/', 
         ProjectVersionViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         }), 
         name='api-project-version-detail'),
    
    path('projects/<int:project_id>/versions/<int:pk>/set-latest/', 
         ProjectVersionViewSet.as_view({'post': 'set_latest'}), 
         name='api-project-version-set-latest'),
    
    path('projects/<int:project_id>/versions/<int:pk>/download/', 
         ProjectVersionViewSet.as_view({'get': 'download'}), 
         name='api-project-version-download'),
]
