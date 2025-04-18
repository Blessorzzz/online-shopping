"""
Material Hazard Index (MHI) Module
----------------------------------
This module handles all calculations and data related to the Material Hazard Index (MHI),
which evaluates the safety of materials used in products.
"""

from django.conf import settings

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


def convert_mhi_to_score(mhi_value: float) -> float:
    """
    Convert the Material Hazard Index (MHI) value (1.0-6.0) to a 0-100 score.
    Higher scores are better (safer).
    """
    score = 100 - (mhi_value - 1) * 16.67
    return round(max(min(score, 100), 0), 2)


def get_material_risk_class(risk_value: float) -> str:
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
    if hasattr(product, 'product_type') and product.product_type != 'tangible':
        return {
            "applicable": False,
            "message": "Safety analysis not applicable for virtual products"
        }
    
    # Get materials - either directly from a list or from a comma-separated string
    if isinstance(product, list):
        materials = product
    else:
        materials = [material.strip() for material in product.materials.split(',')] if hasattr(product, 'materials') and product.materials else []
    
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
        "score": convert_mhi_to_score(overall_risk),
        "risk_category": risk_category,
        "materials": material_hazards,
        "highest_risk_material": highest_risk_material,
        "has_restricted_materials": has_restricted,
        "restricted_materials": restricted_materials,
        "has_banned_materials": has_banned,
        "banned_materials": banned_materials,
        "recommendations": recommendations
    }


def get_material_options():
    """
    Returns a list of available materials for selection in forms.
    """
    materials = []
    
    # Group materials by risk class
    materials_by_class = {
        'A': [],
        'B': [],
        'C': [],
        'D': [],
        'E': [],
        'F': []
    }
    
    for material_key, data in MATERIAL_RISK.items():
        if material_key == 'unknown':
            continue
            
        risk_class = get_material_risk_class(data['risk'])
        
        # Format the material name for display
        display_name = material_key.replace('_', ' ').title()
        
        # Add risk indicator
        display_name = f"{display_name} (Class {risk_class}, {data['risk']})"
        
        materials_by_class[risk_class].append((material_key, display_name))
    
    # Sort each class by name
    for risk_class in materials_by_class:
        materials_by_class[risk_class].sort(key=lambda x: x[1])
    
    # Add class headers and add to main list
    materials.append(('', '--- Class A - Very Low Risk ---'))
    materials.extend(materials_by_class['A'])
    
    materials.append(('', '--- Class B - Low Risk ---'))
    materials.extend(materials_by_class['B'])
    
    materials.append(('', '--- Class C - Moderate Risk ---'))
    materials.extend(materials_by_class['C'])
    
    materials.append(('', '--- Class D - High Risk ---'))
    materials.extend(materials_by_class['D'])
    
    materials.append(('', '--- Class E - Very High Risk ---'))
    materials.extend(materials_by_class['E'])
    
    materials.append(('', '--- Class F - Extreme Risk ---'))
    materials.extend(materials_by_class['F'])
    
    return materials
