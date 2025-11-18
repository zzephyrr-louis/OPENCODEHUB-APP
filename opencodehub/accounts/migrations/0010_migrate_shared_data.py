from django.db import migrations

def migrate_shared_data(apps, schema_editor):
    """Migrate existing shared_with data to SharedProject model"""
    Project = apps.get_model('accounts', 'Project')
    SharedProject = apps.get_model('accounts', 'SharedProject')
    
    for project in Project.objects.all():
        for user in project.shared_with.all():
            # Create SharedProject entry with default 'edit' permission for existing shares
            SharedProject.objects.get_or_create(
                project=project,
                user=user,
                defaults={
                    'permission': 'edit',  # Give edit permission to existing shared users
                    'shared_by': project.owner
                }
            )

def reverse_migrate_shared_data(apps, schema_editor):
    """Reverse migration - copy SharedProject data back to ManyToMany"""
    Project = apps.get_model('accounts', 'Project')
    SharedProject = apps.get_model('accounts', 'SharedProject')
    
    for shared in SharedProject.objects.all():
        shared.project.shared_with.add(shared.user)

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_sharedproject'),
    ]

    operations = [
        migrations.RunPython(migrate_shared_data, reverse_migrate_shared_data),
    ]
