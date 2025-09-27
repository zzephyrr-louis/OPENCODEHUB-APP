from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Project, ProjectFile, ProjectVersion, Comment

# Custom User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'project_count')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    # Add custom fields to the user form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('profile_picture', 'bio', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'date_joined')
    
    def project_count(self, obj):
        """Display number of projects for each user"""
        return obj.projects.count()
    project_count.short_description = 'Projects'

# Project Admin
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin for Project model"""
    list_display = ('title', 'owner', 'is_public', 'file_count', 'version_count', 'comment_count', 'created_at')
    list_filter = ('is_public', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'owner__username')
    list_select_related = ('owner',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Project Info', {
            'fields': ('title', 'description', 'owner', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def file_count(self, obj):
        """Display number of files in project"""
        return obj.files.count()
    file_count.short_description = 'Files'
    
    def version_count(self, obj):
        """Display number of versions"""
        return obj.versions.count()
    version_count.short_description = 'Versions'
    
    def comment_count(self, obj):
        """Display number of comments"""
        return obj.comments.count()
    comment_count.short_description = 'Comments'

# ProjectFile Admin
@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    """Admin for ProjectFile model"""
    list_display = ('name', 'project', 'file_type', 'formatted_size', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('name', 'project__title', 'file_type')
    list_select_related = ('project',)
    date_hierarchy = 'uploaded_at'
    ordering = ('-uploaded_at',)
    
    fieldsets = (
        ('File Info', {
            'fields': ('name', 'project', 'file', 'file_type')
        }),
        ('Details', {
            'fields': ('size', 'uploaded_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('uploaded_at',)
    
    def formatted_size(self, obj):
        """Format file size in human readable format"""
        size = obj.size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    formatted_size.short_description = 'File Size'

# ProjectVersion Admin
@admin.register(ProjectVersion)
class ProjectVersionAdmin(admin.ModelAdmin):
    """Admin for ProjectVersion model"""
    list_display = ('project', 'version_number', 'created_by', 'created_at', 'short_description')
    list_filter = ('created_at', 'created_by')
    search_fields = ('project__title', 'version_number', 'description')
    list_select_related = ('project', 'created_by')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Version Info', {
            'fields': ('project', 'version_number', 'created_by')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at',)
    
    def short_description(self, obj):
        """Display truncated description"""
        if obj.description:
            return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
        return "No description"
    short_description.short_description = 'Description'

# Comment Admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin for Comment model"""
    list_display = ('author', 'project', 'short_content', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('content', 'author__username', 'project__title')
    list_select_related = ('author', 'project')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Comment Info', {
            'fields': ('project', 'author', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def short_content(self, obj):
        """Display truncated comment content"""
        return obj.content[:75] + "..." if len(obj.content) > 75 else obj.content
    short_content.short_description = 'Content'

# Customize admin site headers
admin.site.site_header = "OpenCodeHub Administration"
admin.site.site_title = "OpenCodeHub Admin"
admin.site.index_title = "Welcome to OpenCodeHub Administration"