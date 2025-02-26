from django.db import models
import uuid
from vendor.models import Vendor
from django.utils.translation import gettext_lazy as _
from deep_translator import GoogleTranslator  # 使用 deep-translator 代替 googletrans

class Product(models.Model):
    STATUS_CHOICES = [
        ('stock', _('Stock')),
        ('out_of_stock', _('Out of Stock')),
    ]

    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                   help_text=_('Unique ID for this product across whole shopping mall'))
    product_name = models.CharField(max_length=255, default="", verbose_name=_("Product Name"))
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_active = models.BooleanField(default=True)
    description = models.TextField(default="", verbose_name=_("Description"))
    thumbnail_image = models.ImageField(upload_to='product_thumbnails/', default="https://via.placeholder.com/150")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products', default=1)
    stock_quantity = models.PositiveIntegerField(default=0)
    min_age = models.PositiveIntegerField(default=0, help_text=_("Minimum age suitable for the product"))
    max_age = models.PositiveIntegerField(default=0, help_text=_("Maximum age suitable for the product"))

    def __str__(self):
        return self.product_name

    def stock_status(self):
        return _('Out of Stock') if self.stock_quantity == 0 else f'{self.stock_quantity} ' + _('Available')

    def age_range(self):
        return f'{self.min_age}-{self.max_age} ' + _('years old')

    def save(self, *args, **kwargs):
        """
        如果 product_name 或 description 的翻译字段为空，则自动翻译它们。
        """
        translations = {
            'es': 'es',  # 西班牙语
            'ja': 'ja',  # 日语
            'zh-hans': 'zh-CN'  # 中文
        }

        for lang, dest in translations.items():
            # 处理 product_name
            translated_field = f'product_name_{lang}'
            if hasattr(self, translated_field) and not getattr(self, translated_field):
                setattr(self, translated_field, GoogleTranslator(source='en', target=dest).translate(self.product_name))

            # 处理 description
            translated_field = f'description_{lang}'
            if hasattr(self, translated_field) and not getattr(self, translated_field):
                setattr(self, translated_field, GoogleTranslator(source='en', target=dest).translate(self.description))

        super().save(*args, **kwargs)


class ProductPhoto(models.Model):
    photo_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='product_photos/', default="https://via.placeholder.com/150")

    def __str__(self):
        return f"Photo for {self.product.product_name}"


class ProductVideo(models.Model):
    video_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='product_videos/', null=True, blank=True)

    def __str__(self):
        return f"Video for {self.product.product_name}"
