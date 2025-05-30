# Generated by Django 5.1.5 on 2025-02-26 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0014_rename_description_zh_hans_product_description_zh_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='description_zh',
            new_name='description_zh_hans',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='product_name_zh',
            new_name='product_name_zh_hans',
        ),
        migrations.AlterField(
            model_name='product',
            name='max_age',
            field=models.PositiveIntegerField(default=0, help_text='Maximum age suitable for the product'),
        ),
        migrations.AlterField(
            model_name='product',
            name='min_age',
            field=models.PositiveIntegerField(default=0, help_text='Minimum age suitable for the product'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='product',
            name='stock_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
