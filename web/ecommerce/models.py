from django.db import models
import uuid
from vendor.models import Vendor
from django.utils.translation import gettext_lazy as _
from deep_translator import GoogleTranslator


from django.db import models
import uuid
from vendor.models import Vendor
from django.utils.translation import gettext_lazy as _

class Product(models.Model):
    STATUS_CHOICES = [
        ('stock', _('Stock')),
        ('out_of_stock', _('Out of Stock')),
    ]

    PRODUCT_TYPE_CHOICES = [
        ('tangible', _('Tangible')),
        ('virtual', _('Virtual')),
    ]

    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text=_('Unique ID for this product across whole shopping mall'))
    product_name = models.CharField(max_length=300, default="", verbose_name=_("Product Name"))
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_active = models.BooleanField(default=True)
    description = models.TextField(default="", verbose_name=_("Description"))
    thumbnail_image = models.ImageField(upload_to='product_thumbnails/')
    
    vendor = models.ForeignKey('vendor.Vendor', on_delete=models.CASCADE, related_name='products', default=1)
    
    stock_quantity = models.PositiveIntegerField(default=0)
    min_age = models.PositiveIntegerField(default=0, help_text=_("Minimum age suitable for the product"))
    max_age = models.PositiveIntegerField(default=0, help_text=_("Maximum age suitable for the product"))
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES, default='tangible', verbose_name=_("Product Type"))
    
    warnings = models.TextField(
        blank=True,
        default="",
        help_text=_("Warnings or safety notes related to the product")
    )

    # New materials field
    materials = models.CharField(
        max_length=255, 
        blank=True, 
        default="", 
        help_text=_("Comma-separated list of materials")
    )

    # Safety fields
    safety_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    safety_issues = models.JSONField(null=True, blank=True)  # Store issues like 'small_parts', 'sharp_edges'

    def save(self, *args, **kwargs):
        translations = {
            'es': 'es',
            'ja': 'ja',
            'ko': 'ko',
            'zh-hans': 'zh-CN',
        }

        updated = False
        translatable_fields = ['product_name', 'description']

        # Translation logic for the product name and description
        for lang, dest in translations.items():
            lang_code = lang.replace('-', '_')

            for field in translatable_fields:
                translated_field = f'{field}_{lang_code}'
                source_text = getattr(self, field, "")

                existing_value = getattr(self, translated_field, None)

                if not existing_value or existing_value == source_text:
                    translator = GoogleTranslator(source='auto', target=dest)
                    translated_text = translator.translate(source_text)
                    setattr(self, translated_field, translated_text)
                    updated = True

        # ✅ Ensure stock quantity updates even if no translation changes
        super().save(*args, **kwargs)

        if updated:
            self.refresh_from_db()
            print("✅ Translation updated")
        else:
            print("⚠️ No translation changes")

        # Perform toy safety evaluation here before saving the product
        # Parse materials field and remove leading/trailing spaces from each material
        materials = [material.strip() for material in self.materials.split(',')] if self.materials else []
        detected_hazards = ['small_parts']  # Example: detected hazards (this should come from image analysis or manual input)

        # Calculate MHI, ACR, VHD, ICS
        mhi = calculate_material_risk(materials)  # Make sure the materials are passed correctly
        acr = calculate_age_risk(detected_hazards, (self.min_age, self.max_age))
        vhd = 100  # Placeholder for Visual Hazard Detection score
        ics = calculate_info_score({'materials': self.materials, 'age_range': (self.min_age, self.max_age), 'warnings': self.warnings})

        # Calculate the final safety score using a weighted average
        self.safety_score = (0.25 * mhi + 0.35 * acr + 0.30 * vhd + 0.10 * ics)

        # Save safety issues
        self.safety_issues = detected_hazards  # This can be expanded to include all identified issues

        super().save(*args, **kwargs)


class ProductPhoto(models.Model):
    photo_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='product_photos/')

    def __str__(self):
        return f"Photo for {self.product.product_name}"

class ProductVideo(models.Model):
    video_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='product_videos/', null=True, blank=True)

    def __str__(self):
        return f"Video for {self.product.product_name}"
    

from django.db import models

class SynonymCache(models.Model):
    word = models.CharField(max_length=100, unique=True)
    synonyms = models.TextField()  # 存储JSON字符串
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.word

class KeywordSearchHistory(models.Model):
    """记录用户搜索历史，用于分析和优化关键词提取"""
    original_text = models.TextField()
    extracted_keywords = models.TextField()  # 存储JSON字符串
    expanded_keywords = models.TextField()  # 存储JSON字符串
    successful_search = models.BooleanField(default=False)  # 搜索是否返回结果
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.original_text[:50]
    
# Material Hazard Index Mapping
MATERIAL_RISK = {
    "cotton": 6,  # High safety, contributes more to the score
    "silicone": 5,
    "abs_plastic": 4,
    "pvc": 3,  # Medium risk
    "metal": 2,  # High risk, penalizes score
    "unknown": 1  # Maximum penalty for unknown
}

def calculate_material_risk(materials):
    if not materials:  # If the materials list is empty, return a default risk value (e.g., 1)
        return 6  # Safer materials contribute more to the score
    
    total_risk = 0
    material_count = len(materials)  # Total number of materials

    # Calculate the total risk for the materials
    for material in materials:
        material_risk = MATERIAL_RISK.get(material.lower(), 1)  # Default to 1 if material is not in the dictionary
        total_risk += material_risk
    
    # Calculate the average material risk score
    average_risk = total_risk / material_count

    # Return the final average material risk, ensuring it stays within the safe range
    return min(average_risk, 6)  # Cap it at a maximum of 6 for safety


# Age Hazard Matrix: hazard type and threshold based on age
AGE_HAZARD_MATRIX = {
    'small_parts': {'threshold_age': 3, 'weight': 0.8},
    'sharp_edges': {'threshold_age': 4, 'weight': 0.9},
    'long_cords': {'threshold_age': 6, 'weight': 0.6},
    'toxic_paint': {'threshold_age': 8, 'weight': 0.7}
}

def calculate_age_risk(detected_hazards: list, labeled_age_range: tuple) -> float:
    min_age = labeled_age_range[0]
    risk_score = 0

    for hazard in detected_hazards:
        cfg = AGE_HAZARD_MATRIX[hazard]
        if min_age < cfg['threshold_age']:
            age_gap = cfg['threshold_age'] - min_age
            risk_score += age_gap * cfg['weight'] * 15  # 15 = amplification factor

    return min(max(100 - risk_score, 0), 100)  # Scale from 0 to 100

class VisualSafetyInspector:
    def __init__(self):
        self.hazard_rules = {
            'small_part': {'max_size': 3.5, 'min_confidence': 0.7},
            'sharp_edge': {'min_angle': 60, 'edge_length': 2.0},
            'toxic_material': {'color_range': [(0,50,50), (70,255,255)]}
        }

    def analyze_image(self, img_path: str) -> dict:
        results = {'hazards': [], 'measurements': {}}
        # Placeholder for actual image analysis using OpenCV, etc.
        return results

SAFETY_INFO_REQUIREMENTS = {
    'mandatory': ['materials', 'age_range', 'warnings', 'certification'],
    'recommended': ['country_origin', 'wash_instructions', 'test_standards']
}

def calculate_info_score(product_data: dict) -> float:
    mandatory_missing = [f for f in SAFETY_INFO_REQUIREMENTS['mandatory'] if not product_data.get(f)]
    completeness = (
        0.7 * (1 - len(mandatory_missing) / 4) + 
        0.3 * (sum(1 for f in SAFETY_INFO_REQUIREMENTS['recommended'] if product_data.get(f)) / 3)
    )
    return round(completeness * 100, 1)  # Scale from 0 to 100
