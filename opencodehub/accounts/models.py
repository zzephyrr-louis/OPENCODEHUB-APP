from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
import json

class User(AbstractUser):
    """Extended user model for OpenCodeHub"""
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Security Question for Password Reset
    security_question = models.CharField(max_length=200, blank=True, default='')
    security_answer = models.CharField(max_length=200, blank=True, default='')


class Project(models.Model):
    """Model for user projects"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    shared_with = models.ManyToManyField(User, related_name='shared_projects', blank=True)
    share_link = models.UUIDField(editable=False, unique=True, null=True, blank=True)

    def get_next_version_number(self): 
        """Get the next version number for this project"""
        latest = self.versions.order_by('-version_number').first()
        if latest:
            try:
                current = int(latest.version_number.replace('v', ''))
                return f"v{current + 1}"
            except:
                return "v1"
        return "v1"
    
    def __str__(self):
        return self.title
    
    def get_shareable_link(self):
        """Generate the full shareable URL for this project"""
        return f"/share/{self.share_link}/"

class ProjectFile(models.Model):
    """Model for files within projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='project_files/')
    file_type = models.CharField(max_length=50)
    size = models.IntegerField()
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.project.title} - {self.name}"

class ProjectVersion(models.Model):
    """Model for project version history"""
    ACTION_CHOICES = [
        ('created', 'Project Created'),
        ('file_added', 'File Added'),
        ('file_updated', 'File Updated'),
        ('file_deleted', 'File Deleted'),
        ('shared', 'Project Shared'),
        ('comment_added', 'Comment Added'),
        ('manual', 'Manual Save'),
        ('restored', 'Version Restored'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='manual')
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Store snapshot of files at this version
    files_snapshot = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['project', 'version_number']
    
    def __str__(self):
        return f"{self.project.title} {self.version_number}"
    
    def get_action_display_with_icon(self):
        """Get display text for action"""
        return self.get_action_display()
    
    def create_files_snapshot(self):
        """Create a snapshot of current project files"""
        files_data = []
        for file in self.project.files.all():
            files_data.append({
                'id': file.id,
                'name': file.name,
                'file_url': file.file.url if file.file else None,
                'file_type': file.file_type,
                'size': file.size,
                'uploaded_at': file.uploaded_at.isoformat(),
            })
        self.files_snapshot = {
            'files': files_data,
            'total_files': len(files_data),
            'timestamp': timezone.now().isoformat(),
        }
        self.save()
class Comment(models.Model):
    """Model for project comments"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.project.title}"