# Generated by Django 4.2 on 2025-04-20 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licorera_los_J', '0011_alter_productos_precio'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuarios',
            name='carrito',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
