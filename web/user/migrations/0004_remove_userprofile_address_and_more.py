# Generated by Django 5.1.5 on 2025-02-27 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='address',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='shipping_address',
            field=models.CharField(blank=True, max_length=255, verbose_name='Shipping address'),
        ),
    ]
