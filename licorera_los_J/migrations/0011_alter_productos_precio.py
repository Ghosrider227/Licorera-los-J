# Generated by Django 4.2.20 on 2025-04-04 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licorera_los_J', '0010_alter_usuarios_foto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productos',
            name='precio',
            field=models.IntegerField(),
        ),
    ]
