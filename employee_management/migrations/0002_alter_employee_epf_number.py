# Generated by Django 4.1.13 on 2025-06-22 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='epf_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
