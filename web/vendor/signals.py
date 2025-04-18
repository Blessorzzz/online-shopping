from django.db.models.signals import post_save
from django.dispatch import receiver
from ecommerce.models import Product
from vendor.edge_detector import EdgeSharpnessAnalyzer

@receiver(post_save, sender=Product)
def run_edge_detection_on_new_product(sender, instance, created, **kwargs):
    """Trigger edge detection when a new product is saved."""
    if created:  # This checks if the product is newly created
        # Assuming the image is saved and available at 'instance.thumbnail_image.path'
        # You may adjust this to handle different image fields
        analyzer = EdgeSharpnessAnalyzer(sharp_threshold=0.15, curvature_threshold=1000)
        
        # Run edge detection on the product image
        result = analyzer.analyze_image(instance.thumbnail_image.path, product_id=instance.product_id)
        
        # Optionally, print or log the result
        print(f"Safety Warning for {instance.product_name}: {result['safety_warning']}")