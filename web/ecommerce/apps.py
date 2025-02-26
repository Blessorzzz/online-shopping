from django.apps import AppConfig

class EcommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ecommerce"

    def ready(self):
        import ecommerce.translation  # 确保翻译功能被正确加载

