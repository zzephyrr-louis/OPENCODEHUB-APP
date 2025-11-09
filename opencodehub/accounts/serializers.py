from rest_framework import serializers
from .models import Project, ProjectVersion, ProjectFile, Comment, User
import os
from django.conf import settings


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    profile_picture_url = serializers.SerializerMethodField()
    total_uploads = serializers.SerializerMethodField()
    formatted_upload_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'profile_picture', 'profile_picture_url', 'bio', 
                  'total_uploads', 'formatted_upload_count']
        read_only_fields = ['id', 'total_uploads', 'formatted_upload_count']
    
    def get_profile_picture_url(self, obj):
        """Get profile picture URL with fallback to default"""
        return obj.get_profile_picture_url()
    
    def get_total_uploads(self, obj):
        """Get total upload count for user"""
        return obj.get_total_uploads()
    
    def get_formatted_upload_count(self, obj):
        """Get formatted upload count (e.g., 1.2k, 2M)"""
        count = obj.get_total_uploads()
        return User.format_upload_count(count)


class ProjectFileSerializer(serializers.ModelSerializer):
    """Serializer for ProjectFile model"""
    class Meta:
        model = ProjectFile
        fields = ['id', 'name', 'file', 'file_type', 'size', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class ProjectVersionSerializer(serializers.ModelSerializer):
    """Serializer for ProjectVersion model"""
    created_by = UserSerializer(read_only=True)
    version_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectVersion
        fields = [
            'id', 'project', 'version_number', 'description', 
            'created_at', 'created_by', 'version_file', 'version_file_url',
            'file_size', 'file_type', 'is_latest'
        ]
        read_only_fields = ['id', 'created_at', 'created_by', 'file_size', 'file_type']
    
    def get_version_file_url(self, obj):
        """Get the full URL for the version file"""
        if obj.version_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.version_file.url)
        return None


class ProjectVersionUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading new project versions"""
    version_file = serializers.FileField(required=True)
    
    class Meta:
        model = ProjectVersion
        fields = ['version_number', 'description', 'version_file', 'is_latest']
    
    def validate_version_file(self, value):
        """Validate the uploaded file"""
        # Check file size
        max_size = getattr(settings, 'MAX_FILE_SIZE', 50 * 1024 * 1024)
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size ({value.size / (1024*1024):.1f}MB) exceeds maximum allowed size ({max_size / (1024*1024)}MB)"
            )
        
        # Check file extension
        file_extension = os.path.splitext(value.name)[1].lower()
        blocked_extensions = getattr(settings, 'BLOCKED_FILE_EXTENSIONS', [])
        if file_extension in blocked_extensions:
            raise serializers.ValidationError(
                f"File type {file_extension} is not allowed for security reasons"
            )
        
        return value
    
    def validate_version_number(self, value):
        """Validate version number is unique for the project"""
        project_id = self.context.get('project_id')
        if ProjectVersion.objects.filter(project_id=project_id, version_number=value).exists():
            raise serializers.ValidationError(
                f"Version {value} already exists for this project"
            )
        return value
    
    def create(self, validated_data):
        """Create a new project version"""
        project_id = self.context.get('project_id')
        user = self.context.get('user')
        
        # Extract file information
        version_file = validated_data.get('version_file')
        file_extension = os.path.splitext(version_file.name)[1].lower()
        
        # Handle is_latest flag
        is_latest = validated_data.get('is_latest', False)
        if is_latest:
            # Unmark all other versions as latest
            ProjectVersion.objects.filter(project_id=project_id).update(is_latest=False)
        
        # Create the version
        version = ProjectVersion.objects.create(
            project_id=project_id,
            version_number=validated_data['version_number'],
            description=validated_data.get('description', ''),
            created_by=user,
            version_file=version_file,
            file_size=version_file.size,
            file_type=file_extension[1:] if file_extension else 'unknown',
            is_latest=is_latest
        )
        
        # If no other version is marked as latest, mark this one
        if not is_latest and not ProjectVersion.objects.filter(project_id=project_id, is_latest=True).exists():
            version.is_latest = True
            version.save()
        
        return version


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'project', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model"""
    owner = UserSerializer(read_only=True)
    files = ProjectFileSerializer(many=True, read_only=True)
    versions = ProjectVersionSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    shared_with = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'owner', 'created_at', 
            'updated_at', 'is_public', 'files', 'versions', 
            'comments', 'shared_with', 'share_link'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at', 'share_link']
