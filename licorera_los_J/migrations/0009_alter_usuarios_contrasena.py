# Generated by Django 4.2.20 on 2025-04-04 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licorera_los_J', '0008_alter_productos_foto_alter_usuarios_foto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarios',
            name='contrasena',
            field=models.CharField(default='', max_length=254),
        ),
    ]
