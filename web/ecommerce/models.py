from django.db import models
import uuid
from vendor.models import Vendor
from django.utils.translation import gettext_lazy as _
from deep_translator import GoogleTranslator


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
      translations = {
        'es': 'es',
        'ja': 'ja',
        'ko': 'ko',
        'zh-hans': 'zh-CN',  
    }

      updated = False

    # ✅ 需要翻译的字段列表（新增此行）
      translatable_fields = ['product_name', 'description']

      for lang, dest in translations.items():
        lang_code = lang.replace('-', '_') 

        # ✅ 遍历所有需要翻译的字段（新增循环）
        for field in translatable_fields:
            translated_field = f'{field}_{lang_code}'  # 动态生成字段名（如 description_zh_hans）
            source_text = getattr(self, field)  # 获取原始字段值（如英文 product_name 或 description）

            existing_value = getattr(self, translated_field, None)

            if not existing_value or existing_value == source_text:
                translator = GoogleTranslator(source='auto', target=dest)
                translated_text = translator.translate(source_text)
                setattr(self, translated_field, translated_text)
                updated = True

      if updated:
        super().save(*args, **kwargs)
        self.refresh_from_db()
        print("✅ 翻译已更新")
      else:
        print("⚠️ 没有发现更新，不执行保存")


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
