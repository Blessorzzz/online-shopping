# Generated by Django 5.1.6 on 2025-04-19 08:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0036_alter_product_product_id_alter_product_safety_issues'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='description_es',
        ),
        migrations.RemoveField(
            model_name='product',
            name='description_ko',
        ),
        migrations.RemoveField(
            model_name='product',
            name='product_name_es',
        ),
        migrations.RemoveField(
            model_name='product',
            name='product_name_ko',
        ),
    ]
