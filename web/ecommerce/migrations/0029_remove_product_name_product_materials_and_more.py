# Generated by Django 5.1.6 on 2025-04-04 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0028_keywordsearchhistory_synonymcache'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='name',
        ),
        migrations.AddField(
            model_name='product',
            name='safety_issues',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='safety_score',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),

    ]
