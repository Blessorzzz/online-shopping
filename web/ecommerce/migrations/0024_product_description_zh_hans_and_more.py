# Generated by Django 5.1.5 on 2025-03-01 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0023_remove_product_description_zh_hans_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description_zh_hans',
            field=models.TextField(default='', null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_name_zh_hans',
            field=models.CharField(default='', max_length=255, null=True, verbose_name='Product Name'),
        ),
    ]
