from django.db import migrations

def update_compliance_manager_permissions(apps, schema_editor):
    RBAC = apps.get_model('grc', 'RBAC')
    
    # Update permissions for Compliance Manager role
    RBAC.objects.filter(role='Compliance Manager').update(
        create_framework=True,  # Add framework creation permission
        create_policy=True,     # Also ensure they can create policies
        edit_policy=True,       # And edit policies
        view_all_policy=True,   # And view policies
        policy_performance_analytics=True  # And view analytics
    )

class Migration(migrations.Migration):
    dependencies = [
        ('grc', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_compliance_manager_permissions),
    ] 