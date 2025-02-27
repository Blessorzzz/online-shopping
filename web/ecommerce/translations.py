from modeltranslation.translator import translator, TranslationOptions
from .models import Product

class ProductTranslationOptions(TranslationOptions):
    fields = ('product_name', 'description')  # 添加 product_name

translator.register(Product, ProductTranslationOptions)