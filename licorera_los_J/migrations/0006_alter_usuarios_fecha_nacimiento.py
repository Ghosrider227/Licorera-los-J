# Generated by Django 4.2 on 2025-03-25 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licorera_los_J', '0005_alter_usuarios_fecha_nacimiento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarios',
            name='fecha_nacimiento',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
