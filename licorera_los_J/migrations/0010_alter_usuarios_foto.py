# Generated by Django 4.2.20 on 2025-04-04 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licorera_los_J', '0009_alter_usuarios_contrasena'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarios',
            name='foto',
            field=models.ImageField(blank=True, default='usuario/default.png', null=True, upload_to='usuario/'),
        ),
    ]
