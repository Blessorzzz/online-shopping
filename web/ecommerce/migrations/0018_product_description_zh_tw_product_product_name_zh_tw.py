# Generated by Django 5.1.5 on 2025-02-27 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0017_product_description_ko_product_product_name_ko'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description_zh_TW',
            field=models.TextField(default='', null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_name_zh_TW',
            field=models.CharField(default='', max_length=255, null=True, verbose_name='Product Name'),
        ),
    ]
