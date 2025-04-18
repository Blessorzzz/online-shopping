"""
Age Compliance Risk (ACR) Module
--------------------------------
This module handles all calculations and data related to the Age Compliance Risk (ACR),
which evaluates product safety relative to the intended age range.
"""

from django.conf import settings

# Age Hazard Matrix: hazard type and threshold based on age
AGE_HAZARD_MATRIX = {
    'small_parts': {'threshold_age': 3, 'weight': 0.8},
    'sharp_edges': {'threshold_age': 4, 'weight': 0.9},
    'long_cords': {'threshold_age': 6, 'weight': 0.6},
    'toxic_paint': {'threshold_age': 8, 'weight': 0.7},
    'choking_hazard': {'threshold_age': 3, 'weight': 0.85},
    'suffocation_risk': {'threshold_age': 5, 'weight': 0.9},
    'magnets': {'threshold_age': 6, 'weight': 0.75},
    'batteries': {'threshold_age': 8, 'weight': 0.95}
}

# Age group definitions for recommendation purposes
AGE_GROUPS = {
    'infant': {'min': 0, 'max': 12, 'unit': 'months'},
    'toddler': {'min': 1, 'max': 3, 'unit': 'years'},
    'preschool': {'min': 3, 'max': 5, 'unit': 'years'},
    'school_age': {'min': 5, 'max': 12, 'unit': 'years'},
    'teen': {'min': 12, 'max': 18, 'unit': 'years'}
}

# Special age-related requirements
AGE_REQUIREMENTS = {
    'under_3': [
        'No small parts that fit in a choke tube (< 1.25" diameter, < 2.25" length)',
        'No cords longer than 7 inches',
        'No projectiles or sharp points',
        'No batteries accessible without tools'
    ],
    'under_6': [
        'No accessible magnets that can be swallowed',
        'No high-powered magnets',
        'Supervision required for products with batteries',
        'Limited cord length'
    ],
    'under_8': [
        'Warning labels required for products with small parts',
        'Button/coin batteries must be secure behind screw-fastened compartments',
        'Sharp points/edges must not be accessible'
    ]
}


def calculate_age_risk(detected_hazards: list, labeled_age_range: tuple) -> float:
    """
    Calculate Age Compliance Risk score based on detected hazards and product's labeled age range.
    
    Parameters:
    - detected_hazards: List of hazard types or dictionaries with hazard information
    - labeled_age_range: Tuple of (min_age, max_age) in years
    
    Returns:
    - Risk score from 0-100 (higher is better/safer)
    """
    if not detected_hazards:
        detected_hazards = []
        
    min_age = labeled_age_range[0]
    risk_score = 0

    # We need to handle both string hazards and dictionary hazards
    for hazard in detected_hazards:
        # Extract hazard key - may be a string or a dict with 'type'
        hazard_key = hazard
        if isinstance(hazard, dict) and 'type' in hazard:
            hazard_key = hazard['type']
            
        # Now use the extracted key to look up in the matrix
        cfg = AGE_HAZARD_MATRIX.get(hazard_key, {})
        if cfg and min_age < cfg['threshold_age']:
            age_gap = cfg['threshold_age'] - min_age
            risk_score += age_gap * cfg['weight'] * 15  # Amplification factor

    # Special rule for children under 3 years
    if min_age < 3:
        risk_score += (3 - min_age) * 25

    return min(max(100 - risk_score, 0), 100)  # Scale: 0-100


def get_age_recommendations(labeled_age_range: tuple, detected_hazards: list) -> list:
    """
    Generate age-specific safety recommendations based on product's age range and hazards.
    
    Parameters:
    - labeled_age_range: Tuple of (min_age, max_age) in years
    - detected_hazards: List of hazard types
    
    Returns:
    - List of recommendations
    """
    min_age, max_age = labeled_age_range
    recommendations = []
    
    # Determine which age group the product falls into
    applicable_requirements = []
    if min_age < 3:
        applicable_requirements.extend(AGE_REQUIREMENTS['under_3'])
    if min_age < 6:
        applicable_requirements.extend(AGE_REQUIREMENTS['under_6'])
    if min_age < 8:
        applicable_requirements.extend(AGE_REQUIREMENTS['under_8'])
    
    # Identify potential issues based on age range and hazards
    hazard_keys = [h['type'] if isinstance(h, dict) else h for h in detected_hazards]
    
    # Check for specific hazard combinations with age ranges
    if min_age < 3 and any(h in ['small_parts', 'choking_hazard'] for h in hazard_keys):
        recommendations.append("WARNING: Product contains small parts but is labeled for children under 3 years")
    
    if min_age < 6 and any(h in ['magnets', 'batteries'] for h in hazard_keys):
        recommendations.append("WARNING: Product contains hazards requiring closer supervision for the labeled age range")
    
    # Add general age-appropriate recommendations
    if min_age < 3:
        recommendations.append("Ensure product meets all CPSC requirements for children under 3 years")
    
    if max_age - min_age > 5:
        recommendations.append("Consider narrowing the age range for more targeted safety features")
    
    # Include applicable requirements
    if applicable_requirements:
        recommendations.append("Product must comply with the following age-related requirements:")
        recommendations.extend([f"- {req}" for req in applicable_requirements])
    
    return recommendations


def get_age_compliance_report(product) -> dict:
    """
    Generate a comprehensive age compliance report for a product.
    
    Parameters:
    - product: Product object with age range and safety issue information
    
    Returns:
    - Dictionary containing age compliance analysis
    """
    if hasattr(product, 'product_type') and product.product_type != 'tangible':
        return {
            "applicable": False,
            "message": "Age compliance analysis not applicable for virtual products"
        }
    
    # Get product details
    min_age = product.min_age if hasattr(product, 'min_age') else 0
    max_age = product.max_age if hasattr(product, 'max_age') else 0
    detected_hazards = product.safety_issues if hasattr(product, 'safety_issues') else []
    
    # Calculate ACR score
    acr_score = calculate_age_risk(detected_hazards, (min_age, max_age))
    
    # Generate recommendations
    recommendations = get_age_recommendations((min_age, max_age), detected_hazards)
    
    # Determine age appropriateness level
    if acr_score >= 90:
        age_appropriateness = "Highly appropriate for labeled age range"
    elif acr_score >= 75:
        age_appropriateness = "Appropriate for labeled age range with proper supervision"
    elif acr_score >= 60:
        age_appropriateness = "Somewhat appropriate, but has potential concerns for labeled age range"
    else:
        age_appropriateness = "NOT appropriate for labeled age range"
    
    # Identify critical age-related hazards
    critical_hazards = []
    for hazard in detected_hazards:
        hazard_key = hazard['type'] if isinstance(hazard, dict) else hazard
        cfg = AGE_HAZARD_MATRIX.get(hazard_key, {})
        if cfg and min_age < cfg['threshold_age']:
            critical_hazards.append({
                "type": hazard_key,
                "threshold_age": cfg['threshold_age'],
                "product_min_age": min_age,
                "age_gap": cfg['threshold_age'] - min_age
            })
    
    return {
        "applicable": True,
        "score": acr_score,
        "age_range": (min_age, max_age),
        "age_appropriateness": age_appropriateness,
        "critical_hazards": critical_hazards,
        "recommendations": recommendations,
        "age_requirements": [req for key, reqs in AGE_REQUIREMENTS.items() 
                             if (key == 'under_3' and min_age < 3) or
                                (key == 'under_6' and min_age < 6) or
                                (key == 'under_8' and min_age < 8)
                             for req in reqs]
    }
