from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import FileResponse, Http404
from django.conf import settings
import os
import mimetypes

from .models import Project, ProjectVersion, ProjectFile, Comment, User
from .serializers import (
    ProjectSerializer, 
    ProjectVersionSerializer, 
    ProjectVersionUploadSerializer,
    ProjectFileSerializer,
    CommentSerializer,
    UserSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination class for API views"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for projects
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        Get projects based on user permissions
        """
        user = self.request.user
        # Get projects that are:
        # 1. Owned by the user
        # 2. Shared with the user
        # 3. Public projects
        return Project.objects.filter(
            Q(owner=user) | 
            Q(shared_with=user) | 
            Q(is_public=True)
        ).distinct()
    
    def perform_create(self, serializer):
        """Set the owner when creating a project"""
        serializer.save(owner=self.request.user)


class ProjectVersionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for project versions
    Handles version upload, listing, and management
    """
    serializer_class = ProjectVersionSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get versions for a specific project"""
        project_id = self.kwargs.get('project_id')
        if project_id:
            project = get_object_or_404(Project, id=project_id)
            # Check permissions
            user = self.request.user
            if not (project.owner == user or 
                   user in project.shared_with.all() or 
                   project.is_public):
                return ProjectVersion.objects.none()
            return project.versions.all()
        return ProjectVersion.objects.none()
    
    def get_serializer_class(self):
        """Use different serializer for create action"""
        if self.action == 'create':
            return ProjectVersionUploadSerializer
        return ProjectVersionSerializer
    
    def create(self, request, project_id=None):
        """
        Upload a new version for a project
        Implements requirements 2.2, 2.3, and 2.5
        """
        project = get_object_or_404(Project, id=project_id)
        
        # Check permissions - only owner or shared users can upload
        if project.owner != request.user and request.user not in project.shared_with.all():
            return Response(
                {"error": "You don't have permission to upload versions to this project"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Use the upload serializer with context
        serializer = ProjectVersionUploadSerializer(
            data=request.data,
            context={
                'project_id': project_id,
                'user': request.user,
                'request': request
            }
        )
        
        if serializer.is_valid():
            # Save the version (this handles file storage and database update)
            version = serializer.save()
            
            # Update project's updated_at timestamp
            project.save()
            
            # Return the created version with full serializer
            response_serializer = ProjectVersionSerializer(
                version, 
                context={'request': request}
            )
            return Response(
                response_serializer.data, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def set_latest(self, request, project_id=None, pk=None):
        """
        Mark a specific version as the latest
        Implements requirement 4.2
        """
        project = get_object_or_404(Project, id=project_id)
        version = get_object_or_404(ProjectVersion, id=pk, project=project)
        
        # Check permissions
        if project.owner != request.user:
            return Response(
                {"error": "Only the project owner can set the latest version"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Unmark all other versions
        ProjectVersion.objects.filter(project=project).update(is_latest=False)
        
        # Mark this version as latest
        version.is_latest = True
        version.save()
        
        serializer = ProjectVersionSerializer(version, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def download(self, request, project_id=None, pk=None):
        """
        Download a specific version file
        Implements requirement 5.1 and 5.2
        """
        project = get_object_or_404(Project, id=project_id)
        version = get_object_or_404(ProjectVersion, id=pk, project=project)
        
        # Check permissions (5.4)
        user = request.user
        if not (project.owner == user or 
               user in project.shared_with.all() or 
               project.is_public):
            return Response(
                {"error": "You don't have permission to download this version"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not version.version_file:
            raise Http404("Version file not found")
        
        # Use Django's secure file handling instead of direct path access
        try:
            # Determine content type from file name
            content_type, _ = mimetypes.guess_type(version.version_file.name)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            # Create secure file response using Django's file handling
            response = FileResponse(
                version.version_file.open('rb'),
                content_type=content_type
            )
        except (IOError, OSError):
            raise Http404("File not found on server")
        
        # Set download headers
        filename = f"{project.title}_v{version.version_number}{os.path.splitext(version.version_file.name)[1]}"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response


class ProjectVersionListView(generics.ListAPIView):
    """
    API endpoint to fetch all versions for a specific project
    Implements requirement 3.1 with pagination (3.4)
    """
    serializer_class = ProjectVersionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get all versions for a specific project with sorting"""
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        
        # Check permissions
        user = self.request.user
        if not (project.owner == user or 
               user in project.shared_with.all() or 
               project.is_public):
            return ProjectVersion.objects.none()
        
        # Get sorting parameter
        sort = self.request.query_params.get('sort', '-created_at')
        valid_sorts = ['created_at', '-created_at', 'version_number', '-version_number']
        if sort not in valid_sorts:
            sort = '-created_at'
        
        return project.versions.all().order_by(sort)


class LatestVersionView(generics.RetrieveAPIView):
    """
    API endpoint to get the latest version of a project
    """
    serializer_class = ProjectVersionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get the latest version for a project"""
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        
        # Check permissions
        user = self.request.user
        if not (project.owner == user or 
               user in project.shared_with.all() or 
               project.is_public):
            raise Http404("Project not found")
        
        # Get latest version
        latest_version = project.versions.filter(is_latest=True).first()
        if not latest_version:
            # If no version is marked as latest, get the most recent
            latest_version = project.versions.first()
        
        if not latest_version:
            raise Http404("No versions found for this project")
        
        return latest_version


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_api(request, username=None):
    """
    API endpoint to get user profile information with upload statistics
    Implements Task 4.5.1 - Display total number of uploads
    """
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    serializer = UserSerializer(user, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_api(request):
    """
    API endpoint to get current authenticated user's profile
    """
    serializer = UserSerializer(request.user, context={'request': request})
    return Response(serializer.data)
