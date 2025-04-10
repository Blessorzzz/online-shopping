from django.db import models
import uuid
from vendor.models import Vendor
from django.utils.translation import gettext_lazy as _
from deep_translator import GoogleTranslator
from django.conf import settings

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
    warnings = models.TextField(blank=True, default="", help_text=_("Warnings or safety notes related to the product"))
    materials = models.CharField(max_length=255, blank=True, default="", help_text=_("Comma-separated list of materials"))
    safety_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    safety_issues = models.JSONField(default=list)  # Store issues like 'small_parts', 'sharp_edges', etc.

    def save(self, *args, **kwargs):
        # Translation logic for the product name and description
        translations = {
            'es': 'es',
            'ja': 'ja',
            'ko': 'ko',
            'zh-hans': 'zh-CN',
        }
        updated = False
        translatable_fields = ['product_name', 'description']

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

        # Ensure safety_issues is a list
        if not isinstance(self.safety_issues, list):
            self.safety_issues = []

        # Parse materials
        materials = [material.strip() for material in self.materials.split(',')] if self.materials else []
        mhi = calculate_material_risk(materials)

        # Visual Hazard Detection (placeholder)
        visual_inspector = VisualSafetyInspector()
        visual_results = visual_inspector.analyze_image(self.thumbnail_image.path)
        detected_hazards = visual_results['hazards']

        # Combine manually entered and detected hazards
        if not self.safety_issues:
            self.safety_issues = detected_hazards
        else:
            # Avoid duplicates
            self.safety_issues = list(set(self.safety_issues + detected_hazards))

        # Calculate the impact of safety issues on the safety score
        hazard_penalty = len(self.safety_issues) * 10  # Deduct 10 points per hazard

        # Age Compliance Risk
        acr = calculate_age_risk(self.safety_issues, (self.min_age, self.max_age))

        # Information Completeness Score
        ics = calculate_info_score({
            'materials': self.materials,
            'age_range': (self.min_age, self.max_age),
            'warnings': self.warnings
        })

        # Get weights from settings (with defaults if not defined)
        mhi_weight = getattr(settings, 'MHI_WEIGHT', 25) / 100
        acr_weight = getattr(settings, 'ACR_WEIGHT', 35) / 100
        vhd_weight = getattr(settings, 'VHD_WEIGHT', 30) / 100
        ics_weight = getattr(settings, 'ICS_WEIGHT', 10) / 100

        # Final Safety Score
        self.safety_score = (
            0.25 * (100 - (mhi - 1) * 16.67) +  # Convert MHI to 0-100
            0.35 * acr +
            0.30 * (100 - hazard_penalty) +  # Deduct points based on hazards
            0.10 * ics
        )

        # Ensure the safety score is within the range of 0-100
        self.safety_score = max(min(self.safety_score, 100), 0)

        super().save(*args, **kwargs)

        if updated:
            self.refresh_from_db()
            print("✅ Translation updated")
        else:
            print("⚠️ No translation changes")
    
    def get_mhi_score(self):
        """Calculate and return the Material Hazard Index (MHI) score."""
        materials = [material.strip() for material in self.materials.split(',')] if self.materials else []
        mhi = calculate_material_risk(materials)
        return round(100 - (mhi - 1) * 16.67, 2)  # Convert MHI to 0-100 scale

    def get_acr_score(self):
        """Calculate and return the Age Compliance Risk (ACR) score."""
        return calculate_age_risk(self.safety_issues, (self.min_age, self.max_age))

    def get_vhd_score(self):
        """Calculate and return the Visual Hazard Detection (VHD) score."""
        hazard_penalty = len(self.safety_issues) * 10  # Deduct 10 points per hazard
        return max(100 - hazard_penalty, 0)  # Ensure the score is not negative

    def get_ics_score(self):
        """Calculate and return the Information Completeness Score (ICS)."""
        product_data = {
            'materials': self.materials,
            'age_range': (self.min_age, self.max_age),
            'warnings': self.warnings
        }
        return calculate_info_score(product_data)

    def __str__(self):
        return self.product_name

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
    "cotton": 1,      # Class A - Low risk
    "silicone": 2,    # Class B
    "abs_plastic": 3, # Class C
    "pvc": 4,         # Class D
    "metal": 5,       # Class E - High risk
    "unknown": 6      # Maximum penalty for unknown materials
}

def calculate_material_risk(materials: list) -> float:
    """Calculate weighted average risk for multi-material products"""
    if not materials:
        return 6  # Default to maximum risk if no materials are provided

    total_risk = sum(MATERIAL_RISK.get(material.lower(), 6) for material in materials)
    average_risk = total_risk / len(materials)

    # Ensure the risk stays within the range of 1-6
    return min(max(average_risk, 1), 6)


# Age Hazard Matrix: hazard type and threshold based on age
AGE_HAZARD_MATRIX = {
    'small_parts': {'threshold_age': 3, 'weight': 0.8},
    'sharp_edges': {'threshold_age': 4, 'weight': 0.9},
    'long_cords': {'threshold_age': 6, 'weight': 0.6},
    'toxic_paint': {'threshold_age': 8, 'weight': 0.7}
}

def calculate_age_risk(detected_hazards: list, labeled_age_range: tuple) -> float:
    if not detected_hazards:
        detected_hazards = []
        
    min_age = labeled_age_range[0]
    risk_score = 0

    for hazard in detected_hazards:
        cfg = AGE_HAZARD_MATRIX.get(hazard, {})
        if cfg and min_age < cfg['threshold_age']:
            age_gap = cfg['threshold_age'] - min_age
            risk_score += age_gap * cfg['weight'] * 15  # Amplification factor

    # Special rule for children under 3 years
    if min_age < 3:
        risk_score += (3 - min_age) * 25

    return min(max(100 - risk_score, 0), 100)  # Scale: 0-100


class VisualSafetyInspector:
    def __init__(self):
        self.hazard_rules = {
            'small_part': {'max_size': 3.5, 'min_confidence': 0.7},
            'sharp_edge': {'min_angle': 60, 'edge_length': 2.0},
            'toxic_material': {'color_range': [(0, 50, 50), (70, 255, 255)]}
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
