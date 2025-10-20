from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

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

    # FOR SHARING FUNCTIONALITY
    shared_with = models.ManyToManyField(User, related_name='shared_projects', blank=True)
    share_link = models.UUIDField(editable=False, unique=True, null=True, blank=True)

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
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.title} v{self.version_number}"

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