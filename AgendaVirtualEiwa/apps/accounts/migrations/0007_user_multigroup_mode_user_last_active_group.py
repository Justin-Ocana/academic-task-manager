# Generated manually for multigroup feature
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_user_completed_range_user_overdue_range_and_more'),
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='multigroup_mode',
            field=models.CharField(
                choices=[('separated', 'Mantener grupos separados'), ('unified', 'Unificar todos los grupos')],
                default='separated',
                max_length=10,
                verbose_name='Modo de visualización multigrupo'
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='last_active_group',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='last_active_users',
                to='groups.group',
                verbose_name='Último grupo activo'
            ),
        ),
    ]
