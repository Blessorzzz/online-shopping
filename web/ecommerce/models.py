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

        # Only apply safety analysis for tangible products
        if self.product_type == 'tangible':
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
        if self.product_type != 'tangible':
            return None  # Not applicable for virtual products
    
        materials = [material.strip() for material in self.materials.split(',')] if self.materials else []
        mhi = calculate_material_risk(materials)
        return round(100 - (mhi - 1) * 16.67, 2)  # Convert MHI to 0-100 scale
    
    def get_material_safety_report(self):
        """Generate a comprehensive material safety report for this product."""
        if self.product_type != 'tangible':
            return {
                "applicable": False,
                "message": "Material safety analysis not applicable for virtual products"
            }
        
        return get_material_summary_for_product(self)

    def get_acr_score(self):
        """Calculate and return the Age Compliance Risk (ACR) score."""
        if self.product_type != 'tangible':
            return None  # Not applicable for virtual products
        
        return calculate_age_risk(self.safety_issues, (self.min_age, self.max_age))

    def get_vhd_score(self):
        """Calculate and return the Visual Hazard Detection (VHD) score."""
        if self.product_type != 'tangible':
            return None  # Not applicable for virtual products
        
        hazard_penalty = len(self.safety_issues) * 10  # Deduct 10 points per hazard
        return max(100 - hazard_penalty, 0)  # Ensure the score is not negative

    def get_ics_score(self):
        """Calculate and return the Information Completeness Score (ICS)."""
        if self.product_type != 'tangible':
            return None  # Not applicable for virtual products
        
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
    
# Expanded Material Hazard Index Mapping with regulatory information
MATERIAL_RISK = {
    # Class A - Very Low Risk (1.0-1.5)
    "cotton": {
        "risk": 1.0, 
        "category": "natural_fiber",
        "standards": ["GOTS", "OEKO-TEX"],
        "regions": ["global"]
    },
    "wool": {
        "risk": 1.1, 
        "category": "natural_fiber",
        "standards": ["OEKO-TEX"],
        "regions": ["global"]
    },
    "silk": {
        "risk": 1.0, 
        "category": "natural_fiber",
        "standards": ["OEKO-TEX"],
        "regions": ["global"]
    },
    "bamboo": {
        "risk": 1.2, 
        "category": "natural_fiber",
        "standards": ["OEKO-TEX"],
        "regions": ["global"]
    },
    "natural_rubber": {
        "risk": 1.5, 
        "category": "natural_polymer",
        "standards": ["FSC"],
        "allergen": True,
        "regions": ["global"]
    },
    "food_grade_silicone": {
        "risk": 1.3, 
        "category": "synthetic_polymer",
        "standards": ["FDA", "EU 10/2011"],
        "regions": ["US", "EU"]
    },
    "organic_cotton": {
        "risk": 1.0, 
        "category": "natural_fiber",
        "standards": ["GOTS", "USDA Organic"],
        "regions": ["global", "US"]
    },
    "linen": {
        "risk": 1.0, 
        "category": "natural_fiber",
        "standards": ["OEKO-TEX"],
        "regions": ["global"]
    },
    "felt": {
        "risk": 1.2, 
        "category": "natural_fiber",
        "standards": ["OEKO-TEX"],
        "regions": ["global"]
    },
    "cork": {
        "risk": 1.1, 
        "category": "natural_material",
        "standards": ["FSC"],
        "regions": ["global"]
    },
    
    # Class B - Low Risk (1.6-2.5)
    "silicone": {
        "risk": 2.0, 
        "category": "synthetic_polymer",
        "standards": ["FDA", "EU 10/2011"],
        "regions": ["US", "EU"]
    },
    "abs_plastic": {
        "risk": 2.2, 
        "category": "synthetic_polymer",
        "standards": ["ASTM F963", "EN 71-3"],
        "notes": "Acrylonitrile Butadiene Styrene",
        "regions": ["US", "EU"]
    },
    "polypropylene": {
        "risk": 1.8, 
        "category": "synthetic_polymer",
        "standards": ["FDA", "EU 10/2011"],
        "notes": "PP",
        "regions": ["US", "EU"]
    },
    "high_density_polyethylene": {
        "risk": 1.7, 
        "category": "synthetic_polymer",
        "standards": ["FDA", "EU 10/2011"],
        "notes": "HDPE",
        "regions": ["US", "EU"]
    },
    "eva_foam": {
        "risk": 2.3, 
        "category": "synthetic_polymer",
        "standards": ["ASTM F963", "EN 71"],
        "notes": "Ethylene-vinyl acetate",
        "regions": ["US", "EU"]
    },
    "polyester": {
        "risk": 2.0, 
        "category": "synthetic_fiber",
        "standards": ["OEKO-TEX"],
        "regions": ["global"]
    },
    "nylon": {
        "risk": 2.2, 
        "category": "synthetic_fiber",
        "standards": ["OEKO-TEX"],
        "regions": ["global"]
    },
    "acrylic": {
        "risk": 2.4, 
        "category": "synthetic_fiber",
        "standards": ["OEKO-TEX"],
        "regions": ["global"]
    },
    "polycarbonate": {
        "risk": 2.5, 
        "category": "synthetic_polymer",
        "standards": ["FDA", "EU 10/2011"],
        "regions": ["US", "EU"]
    },
    "wood": {
        "risk": 2.1, 
        "category": "natural_material",
        "standards": ["FSC", "ASTM F963", "EN 71"],
        "notes": "Treated wood, may have some chemicals",
        "regions": ["global", "US", "EU"]
    },
    
    # Class C - Moderate Risk (2.6-3.5)
    "low_density_polyethylene": {
        "risk": 2.7, 
        "category": "synthetic_polymer",
        "standards": ["FDA", "EU 10/2011"],
        "notes": "LDPE",
        "regions": ["US", "EU"]
    },
    "polyurethane": {
        "risk": 3.0, 
        "category": "synthetic_polymer",
        "standards": ["CertiPUR-US"],
        "notes": "PU",
        "regions": ["US"]
    },
    "leather": {
        "risk": 3.2, 
        "category": "animal_derived",
        "standards": ["REACH"],
        "notes": "Due to tanning chemicals",
        "regions": ["EU"]
    },
    "synthetic_leather": {
        "risk": 3.3, 
        "category": "synthetic_material",
        "standards": ["REACH"],
        "regions": ["EU"]
    },
    "painted_wood": {
        "risk": 3.0, 
        "category": "natural_material",
        "standards": ["ASTM F963", "EN 71-3"],
        "notes": "Depends on paint used",
        "testing_required": ["lead", "heavy_metals"],
        "regions": ["US", "EU"]
    },
    "rubber": {
        "risk": 3.1, 
        "category": "synthetic_polymer",
        "standards": ["ASTM F963", "EN 71"],
        "notes": "Non-natural rubber",
        "regions": ["US", "EU"]
    },
    "melamine": {
        "risk": 3.3, 
        "category": "synthetic_polymer",
        "standards": ["FDA", "EU 10/2011"],
        "testing_required": ["migration_limits"],
        "regions": ["US", "EU"]
    },
    "polystyrene": {
        "risk": 3.2, 
        "category": "synthetic_polymer",
        "standards": ["ASTM F963"],
        "notes": "PS",
        "regions": ["US"]
    },
    "urea_formaldehyde": {
        "risk": 3.5, 
        "category": "synthetic_resin",
        "standards": ["CARB Phase 2", "EPA TSCA Title VI"],
        "notes": "Used in some adhesives",
        "regions": ["US"]
    },
    
    # Class D - High Risk (3.6-4.5)
    "pvc": {
        "risk": 4.0, 
        "category": "synthetic_polymer",
        "standards": ["CPSIA", "REACH", "RoHS"],
        "notes": "Polyvinyl chloride, often contains phthalates",
        "testing_required": ["phthalates", "lead", "cadmium"],
        "regions": ["US", "EU"]
    },
    "pvc_with_phthalates": {
        "risk": 4.5, 
        "category": "synthetic_polymer",
        "standards": ["CPSIA", "REACH", "RoHS"],
        "notes": "PVC with confirmed phthalates",
        "restricted": True,
        "testing_required": ["phthalates", "lead", "cadmium"],
        "regions": ["US", "EU"]
    },
    "formaldehyde_resin": {
        "risk": 4.1, 
        "category": "synthetic_resin",
        "standards": ["CARB Phase 2", "EPA TSCA Title VI"],
        "testing_required": ["formaldehyde_emission"],
        "regions": ["US"]
    },
    "flame_retardant_fabric": {
        "risk": 4.2, 
        "category": "treated_material",
        "standards": ["CPSIA", "REACH"],
        "testing_required": ["PBDE", "TBBPA", "TCEP"],
        "regions": ["US", "EU"]
    },
    "lead_paint": {
        "risk": 4.5, 
        "category": "metal_compound",
        "standards": ["CPSIA", "EN 71-3"],
        "notes": "Pre-ban paint (historical items)",
        "restricted": True,
        "testing_required": ["lead_content"],
        "regions": ["US", "EU"]
    },
    "bpa_plastic": {
        "risk": 4.3, 
        "category": "synthetic_polymer",
        "standards": ["FDA", "EU 2011/8/EU"],
        "notes": "Bisphenol A containing plastics",
        "restricted": True,
        "testing_required": ["BPA_migration"],
        "regions": ["US", "EU"]
    },
    "metal_alloys": {
        "risk": 3.8, 
        "category": "metal",
        "standards": ["ASTM F963", "EN 71-3"],
        "notes": "Mixed metals, possible lead content",
        "testing_required": ["heavy_metals"],
        "regions": ["US", "EU"]
    },
    
    # Class E - Very High Risk (4.6-5.5)
    "metal": {
        "risk": 4.7, 
        "category": "metal",
        "standards": ["ASTM F963", "EN 71-3"],
        "notes": "Generic unknown metal",
        "testing_required": ["heavy_metals", "lead", "cadmium", "chromium"],
        "regions": ["US", "EU"]
    },
    "lead": {
        "risk": 5.5, 
        "category": "metal",
        "standards": ["CPSIA", "EN 71-3"],
        "restricted": True,
        "banned_regions": ["US", "EU", "CA", "AU"],
        "regions": ["global"]
    },
    "cadmium": {
        "risk": 5.4, 
        "category": "metal",
        "standards": ["CPSIA", "EN 71-3", "REACH"],
        "restricted": True,
        "banned_regions": ["US", "EU", "CA", "AU"],
        "regions": ["global"]
    },
    "mercury": {
        "risk": 5.5, 
        "category": "metal",
        "standards": ["CPSIA", "EN 71-3", "REACH"],
        "restricted": True,
        "banned_regions": ["US", "EU", "CA", "AU", "JP"],
        "regions": ["global"]
    },
    "arsenic": {
        "risk": 5.5, 
        "category": "metalloid",
        "standards": ["CPSIA", "EN 71-3", "REACH"],
        "restricted": True,
        "banned_regions": ["US", "EU", "CA", "AU"],
        "regions": ["global"]
    },
    "antimony": {
        "risk": 5.3, 
        "category": "metalloid",
        "standards": ["CPSIA", "EN 71-3", "REACH"],
        "restricted": True,
        "testing_required": ["migration_limits"],
        "regions": ["US", "EU"]
    },
    "chromium": {
        "risk": 5.0, 
        "category": "metal",
        "standards": ["CPSIA", "EN 71-3", "REACH"],
        "notes": "Especially hexavalent chromium",
        "restricted": True,
        "testing_required": ["migration_limits", "speciation"],
        "regions": ["US", "EU"]
    },
    "nickel": {
        "risk": 4.8, 
        "category": "metal",
        "standards": ["EN 1811", "REACH"],
        "notes": "Common allergen",
        "allergen": True,
        "testing_required": ["migration_limits"],
        "regions": ["EU"]
    },
    "beryllium": {
        "risk": 5.2, 
        "category": "metal",
        "standards": ["OSHA", "REACH"],
        "restricted": True,
        "regions": ["US", "EU"]
    },
    
    # Class F - Extreme Risk/Prohibited (5.6-6.0)
    "asbestos": {
        "risk": 6.0, 
        "category": "mineral",
        "standards": ["CPSIA", "REACH"],
        "restricted": True,
        "banned": True,
        "banned_regions": ["US", "EU", "CA", "AU", "JP", "CN"],
        "regions": ["global"]
    },
    "radioactive_materials": {
        "risk": 6.0, 
        "category": "radioactive",
        "restricted": True,
        "banned": True,
        "banned_regions": ["global"],
        "regions": ["global"]
    },
    "dioxins": {
        "risk": 6.0, 
        "category": "chemical_compound",
        "standards": ["Stockholm Convention"],
        "restricted": True,
        "banned": True,
        "banned_regions": ["global"],
        "regions": ["global"]
    },
    "pcbs": {
        "risk": 6.0, 
        "category": "chemical_compound",
        "standards": ["Stockholm Convention", "TSCA"],
        "notes": "Polychlorinated biphenyls",
        "restricted": True,
        "banned": True,
        "banned_regions": ["global"],
        "regions": ["global"]
    },
    "unknown": {
        "risk": 6.0, 
        "category": "unknown",
        "notes": "Maximum penalty for unknown materials",
        "testing_required": ["full_safety_assessment"],
        "regions": ["global"]
    }
}

# Dictionary of global safety standards with descriptions
SAFETY_STANDARDS = {
    "CPSIA": {
        "name": "Consumer Product Safety Improvement Act",
        "region": "US",
        "description": "U.S. law establishing safety standards for children's products",
        "website": "https://www.cpsc.gov/Regulations-Laws--Standards/Statutes/The-Consumer-Product-Safety-Improvement-Act"
    },
    "ASTM F963": {
        "name": "ASTM F963 Toy Safety Standard",
        "region": "US",
        "description": "Standard Consumer Safety Specification for Toy Safety",
        "website": "https://www.astm.org/f0963-17.html"
    },
    "EN 71": {
        "name": "European Safety of Toys",
        "region": "EU",
        "description": "Safety requirements for toys sold in the European Union",
        "website": "https://ec.europa.eu/growth/sectors/toys/safety_en"
    },
    "REACH": {
        "name": "Registration, Evaluation, Authorization and Restriction of Chemicals",
        "region": "EU",
        "description": "EU regulation addressing the production and use of chemical substances",
        "website": "https://echa.europa.eu/regulations/reach/understanding-reach"
    },
    "OEKO-TEX": {
        "name": "OEKO-TEX Standard 100",
        "region": "global",
        "description": "Global testing and certification system for textiles",
        "website": "https://www.oeko-tex.com/en/our-standards/standard-100-by-oeko-tex"
    },
    "GOTS": {
        "name": "Global Organic Textile Standard",
        "region": "global",
        "description": "Leading textile processing standard for organic fibers",
        "website": "https://global-standard.org/"
    },
    "FSC": {
        "name": "Forest Stewardship Council",
        "region": "global",
        "description": "Certification for responsibly managed forests",
        "website": "https://fsc.org/"
    },
    "RoHS": {
        "name": "Restriction of Hazardous Substances",
        "region": "EU",
        "description": "Restricts the use of specific hazardous materials in electronics",
        "website": "https://ec.europa.eu/environment/topics/waste-and-recycling/rohs-directive_en"
    }
}

# Material category explanations for user-friendly display
MATERIAL_RISK_CATEGORIES = {
    "1": {
        "name": "Class A - Very Low Risk",
        "description": "Natural, hypoallergenic materials safe for all ages including infants.",
        "rating": "1.0-1.5",
        "examples": ["cotton", "wool", "silk", "bamboo"],
        "suitable_for": "All ages including infants and children with sensitivities",
        "common_in": "Baby toys, teethers, bedding, clothing"
    },
    "2": {
        "name": "Class B - Low Risk",
        "description": "Common synthetic materials generally considered safe with minimal health concerns.",
        "rating": "1.6-2.5",
        "examples": ["silicone", "polypropylene", "ABS plastic", "HDPE"],
        "suitable_for": "Most age groups",
        "common_in": "Building blocks, food containers, most plastic toys"
    },
    "3": {
        "name": "Class C - Moderate Risk",
        "description": "Materials that may contain trace chemicals or pose moderate risks to certain age groups.",
        "rating": "2.6-3.5",
        "examples": ["polyurethane", "leather", "painted wood", "rubber"],
        "suitable_for": "Children over 3 years with normal supervision",
        "common_in": "Action figures, toy cars, sports equipment"
    },
    "4": {
        "name": "Class D - High Risk",
        "description": "Materials known to potentially contain harmful chemicals or pose physical hazards.",
        "rating": "3.6-4.5",
        "examples": ["PVC", "metal alloys", "flame retardant fabrics"],
        "suitable_for": "Older children with proper supervision",
        "common_in": "Certain electronics, some outdoor equipment",
        "warnings": ["May require additional testing", "Should be avoided in mouthable products"]
    },
    "5": {
        "name": "Class E - Very High Risk",
        "description": "Materials with known toxicity, allergenicity, or other significant health hazards.",
        "rating": "4.6-5.5",
        "examples": ["lead", "cadmium", "chromium", "nickel"],
        "suitable_for": "Limited applications with strict controls",
        "common_in": "Historical items, products requiring special properties",
        "warnings": ["Should be avoided in children's products", "May be subject to strict regulations"]
    },
    "6": {
        "name": "Class F - Extreme Risk/Prohibited",
        "description": "Materials banned or severely restricted in children's products due to extreme toxicity.",
        "rating": "5.6-6.0",
        "examples": ["asbestos", "radioactive materials", "PCBs", "dioxins"],
        "suitable_for": "Not suitable for any children's products",
        "warnings": ["Banned in most countries", "Requires immediate remediation if detected"]
    }
}

# Updated calculation function to use the new dictionary structure
def calculate_material_risk(materials: list) -> float:
    """Calculate weighted average risk for multi-material products"""
    if not materials:
        return 6.0  # Default to maximum risk if no materials are provided
    
    # Normalize material names for matching with the database
    normalized_materials = []
    for material in materials:
        # Convert spaces to underscores and lowercase
        normalized = material.strip().lower().replace(" ", "_")
        normalized_materials.append(normalized)
    
    # Calculate risk using normalized names
    risks = []
    for material in normalized_materials:
        material_data = MATERIAL_RISK.get(material, MATERIAL_RISK["unknown"])
        risks.append(material_data["risk"])
    
    # Higher risk materials are weighted more in the calculation
    # This ensures that one high-risk material isn't diluted by multiple low-risk ones
    weighted_risks = [risk ** 1.5 for risk in risks]  # Apply power weighting
    weighted_avg = sum(weighted_risks) / sum(1 for _ in weighted_risks)
    
    # Convert back to original scale (approx)
    final_risk = weighted_avg ** (1/1.5)
    
    # Ensure the risk stays within the range of 1-6
    return min(max(round(final_risk, 1), 1.0), 6.0)

def get_material_risk_class(risk_value):
    """Return the risk class (A-F) based on the numeric risk value."""
    if 1.0 <= risk_value <= 1.5:
        return "A"
    elif 1.6 <= risk_value <= 2.5:
        return "B"
    elif 2.6 <= risk_value <= 3.5:
        return "C"
    elif 3.6 <= risk_value <= 4.5:
        return "D"
    elif 4.6 <= risk_value <= 5.5:
        return "E"
    else:
        return "F"

def get_material_hazard_info(materials: list) -> dict:
    """Return detailed information about material hazards for the provided materials."""
    if not materials:
        return {"unknown": {
            "risk_class": "F",
            "risk_value": 6.0,
            "name": "Unknown",
            "reasons": ["No material information provided"],
            "standards": [],
            "recommended_testing": ["full_safety_assessment"]
        }}
    
    hazard_info = {}
    
    for material in materials:
        normalized = material.strip().lower().replace(" ", "_")
        
        # Get material data or use unknown as default
        material_data = MATERIAL_RISK.get(normalized, MATERIAL_RISK["unknown"])
        risk_value = material_data["risk"]
        risk_class = get_material_risk_class(risk_value)
        
        # Gather testing recommendations if any
        testing_required = material_data.get("testing_required", [])
        
        # Collect applicable standards
        standards = material_data.get("standards", [])
        standard_details = []
        for std in standards:
            if std in SAFETY_STANDARDS:
                standard_details.append({
                    "code": std,
                    "name": SAFETY_STANDARDS[std]["name"],
                    "region": SAFETY_STANDARDS[std]["region"],
                    "website": SAFETY_STANDARDS[std]["website"]
                })
        
        # Check if material is restricted or banned
        restricted = material_data.get("restricted", False)
        banned = material_data.get("banned", False)
        banned_regions = material_data.get("banned_regions", [])
        
        # Special cases - allergenic materials
        allergen = material_data.get("allergen", False)
        
        # Build reasons list based on material properties
        reasons = []
        if restricted:
            reasons.append("Subject to regulatory restrictions")
        if banned:
            reasons.append("Banned in children's products")
        if allergen:
            reasons.append("Known allergen, may cause reactions in sensitive individuals")
        if material_data.get("notes"):
            reasons.append(material_data["notes"])
            
        # Add to hazard info dictionary
        hazard_info[material] = {
            "risk_class": risk_class,
            "risk_value": risk_value,
            "name": material,
            "category": material_data.get("category", "unknown"),
            "reasons": reasons,
            "standards": standard_details,
            "regions_affected": material_data.get("regions", []),
            "banned_regions": banned_regions,
            "recommended_testing": testing_required,
            "allergen": allergen,
            "restricted": restricted,
            "banned": banned
        }
    
    return hazard_info

def get_material_summary_for_product(product) -> dict:
    """Get a comprehensive material risk summary for a product."""
    if product.product_type != 'tangible':
        return {
            "applicable": False,
            "message": "Safety analysis not applicable for virtual products"
        }
    
    materials = [material.strip() for material in product.materials.split(',')] if product.materials else []
    
    if not materials:
        return {
            "applicable": True,
            "risk_level": "High Risk",
            "risk_class": "F",
            "risk_value": 6.0,
            "message": "No materials specified - unable to assess material safety",
            "materials": {},
            "highest_risk_material": "unknown",
            "recommendations": [
                "Provide detailed material information",
                "Submit product for laboratory testing"
            ]
        }
    
    # Get detailed hazard info for each material
    material_hazards = get_material_hazard_info(materials)
    
    # Find highest risk material
    highest_risk = 0
    highest_risk_material = None
    for material, info in material_hazards.items():
        if info["risk_value"] > highest_risk:
            highest_risk = info["risk_value"]
            highest_risk_material = material
    
    # Calculate overall risk
    overall_risk = calculate_material_risk(materials)
    risk_class = get_material_risk_class(overall_risk)
    
    # Get risk category information
    risk_category = MATERIAL_RISK_CATEGORIES[str(int(overall_risk))]
    
    # Determine if any materials are restricted or banned
    has_restricted = False
    has_banned = False
    restricted_materials = []
    banned_materials = []
    
    for material, info in material_hazards.items():
        if info.get("restricted"):
            has_restricted = True
            restricted_materials.append(material)
        if info.get("banned"):
            has_banned = True
            banned_materials.append(material)
    
    # Generate recommendations
    recommendations = []
    if has_banned:
        recommendations.append("URGENT: Replace banned materials immediately")
    if has_restricted:
        recommendations.append("Consider alternatives for restricted materials")
    if overall_risk > 3.0:
        recommendations.append("Conduct third-party safety testing")
    if overall_risk > 4.0:
        recommendations.append("Implement additional warning labels")
    
    # For Class A and B materials, provide positive feedback
    if overall_risk <= 2.5:
        recommendations.append("Current material selection is appropriate for children's products")
    
    return {
        "applicable": True,
        "risk_level": risk_category["name"],
        "risk_class": risk_class,
        "risk_value": overall_risk,
        "risk_category": risk_category,
        "materials": material_hazards,
        "highest_risk_material": highest_risk_material,
        "has_restricted_materials": has_restricted,
        "restricted_materials": restricted_materials,
        "has_banned_materials": has_banned,
        "banned_materials": banned_materials,
        "recommendations": recommendations
    }

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
