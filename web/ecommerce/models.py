from django.db import models
import uuid
from vendor.models import Vendor
from django.utils.translation import gettext_lazy as _
from deep_translator import GoogleTranslator
from django.conf import settings

# Import the safety modules
from .safety.mhi import calculate_material_risk, get_material_summary_for_product, convert_mhi_to_score
from .safety.acr import calculate_age_risk, AGE_HAZARD_MATRIX
from .safety.vhd import VisualSafetyInspector
from .safety.ics import calculate_info_score

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
    sharpness_category_score = models.PositiveIntegerField(default=0, help_text=_("Sharpness category score (1=Dull, 3=Medium, 5=Sharp)"))
    vhd_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text=_("Visual Hazard Detection score"))

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

        # Only apply safety analysis for tangible products
        if self.product_type == 'tangible':
            # Ensure safety_issues is a list
            if not isinstance(self.safety_issues, list):
                self.safety_issues = []

            # Parse materials
            materials = [material.strip() for material in self.materials.split(',')] if self.materials else []
            mhi = calculate_material_risk(materials)

            # Visual Hazard Detection
            visual_inspector = VisualSafetyInspector()
            visual_results = visual_inspector.analyze_image(self.thumbnail_image.path)
            detected_hazards = visual_results['hazards']

            # Combine manually entered and detected hazards
            if not self.safety_issues:
                self.safety_issues = detected_hazards
            else:
                # Avoid duplicates
                combined_issues = self.safety_issues.copy()
                for hazard in detected_hazards:
                    if hazard not in combined_issues:
                        combined_issues.append(hazard)
                self.safety_issues = combined_issues

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
                mhi_weight * (100 - (mhi - 1) * 16.67) +  # Convert MHI to 0-100
                acr_weight * acr +
                vhd_weight * (100 - hazard_penalty) +  # Deduct points based on hazards
                ics_weight * ics
            )

            # Ensure the safety score is within the range of 0-100
            self.safety_score = max(min(self.safety_score, 100), 0)
        else:
            # For virtual products, set safety-related fields to appropriate defaults
            self.safety_score = None  # No safety score for virtual products
            self.safety_issues = []   # No safety issues for virtual products

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
        if self.sharpness_category_score:
            vhd_score = (100 - hazard_penalty) * 0.7 + (self.sharpness_category_score * 20 * 0.3)
        else:
            vhd_score = 100 - hazard_penalty
        return round(max(vhd_score, 0), 2)  # Ensure the score is not negative

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


class SynonymCache(models.Model):
    word = models.CharField(max_length=100, unique=True)
    synonyms = models.TextField()  # Store JSON string
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.word


class KeywordSearchHistory(models.Model):
    """Record user search history for analysis and keyword optimization."""
    original_text = models.TextField()
    extracted_keywords = models.TextField()  # Store JSON string
    expanded_keywords = models.TextField()  # Store JSON string
    successful_search = models.BooleanField(default=False)  # Whether the search returned results
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.original_text[:50]
