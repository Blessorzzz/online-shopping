# Generated by Django 5.1.5 on 2025-02-25 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0012_alter_productphoto_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description_en',
            field=models.TextField(default='', null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='product',
            name='description_es',
            field=models.TextField(default='', null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='product',
            name='description_ja',
            field=models.TextField(default='', null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='product',
            name='description_zh_hans',
            field=models.TextField(default='', null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_name_en',
            field=models.CharField(default='', max_length=255, null=True, verbose_name='Product Name'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_name_es',
            field=models.CharField(default='', max_length=255, null=True, verbose_name='Product Name'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_name_ja',
            field=models.CharField(default='', max_length=255, null=True, verbose_name='Product Name'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_name_zh_hans',
            field=models.CharField(default='', max_length=255, null=True, verbose_name='Product Name'),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(default='', verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_name',
            field=models.CharField(default='', max_length=255, verbose_name='Product Name'),
        ),
    ]
