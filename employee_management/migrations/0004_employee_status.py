# Generated by Django 3.1.12 on 2025-02-09 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee_management', '0003_auto_20250209_1308'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Disable'), (1, 'Enable')], default=1),
        ),
    ]
