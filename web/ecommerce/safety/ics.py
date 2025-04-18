"""
Information Completeness Score (ICS) Module
-------------------------------------------
This module evaluates the completeness of safety information provided for products.
The completeness of safety information is a key factor in overall product safety,
as proper warnings and instructions help ensure appropriate product use.
"""

from django.conf import settings

# Define information requirements for safety documentation
SAFETY_INFO_REQUIREMENTS = {
    'mandatory': [
        'materials',       # Product material composition
        'age_range',       # Recommended age range
        'warnings',        # Safety warnings and precautions
        'certification'    # Safety certifications
    ],
    'recommended': [
        'country_origin',       # Manufacturing country
        'wash_instructions',    # Cleaning and maintenance
        'test_standards'        # Testing standards compliance
    ],
    'optional': [
        'assembly_instructions', # How to assemble product safely
        'disposal_instructions', # How to dispose of product safely
        'allergen_information'   # Information about potential allergens
    ]
}

# Weights for different information categories
INFO_CATEGORY_WEIGHTS = {
    'mandatory': 0.7,      # 70% of score
    'recommended': 0.2,    # 20% of score
    'optional': 0.1        # 10% of score
}

# Information field descriptions for user guidance
INFO_FIELD_DESCRIPTIONS = {
    'materials': 'Complete list of materials used in product construction',
    'age_range': 'Minimum and maximum age recommendation',
    'warnings': 'Safety warnings, precautions, and usage limitations',
    'certification': 'Safety certifications and compliance declarations',
    'country_origin': 'Country where the product was manufactured',
    'wash_instructions': 'Instructions for cleaning and maintaining the product',
    'test_standards': 'Testing standards the product complies with',
    'assembly_instructions': 'Instructions for safe product assembly',
    'disposal_instructions': 'Instructions for proper product disposal',
    'allergen_information': 'Information about potential allergens in the product'
}

# Quality assessment criteria for each field
FIELD_QUALITY_CRITERIA = {
    'materials': {
        'min_length': 3,
        'recommended_length': 10,
        'contains_keywords': ['made from', 'contains', 'material', '%']
    },
    'warnings': {
        'min_length': 20,
        'recommended_length': 100,
        'contains_keywords': ['warning', 'caution', 'danger', 'not suitable', 'supervision']
    },
    'age_range': {
        'has_both_min_max': True,
        'specifies_years_months': True
    }
}


def calculate_info_score(product_data: dict) -> float:
    """
    Calculate the Information Completeness Score (ICS) for a product.
    
    Args:
        product_data: Dictionary containing product information fields
        
    Returns:
        Completeness score on a scale of 0-100
    """
    # Check for empty input
    if not product_data:
        return 0.0
        
    # Track completeness by category
    category_scores = {
        'mandatory': 0.0,
        'recommended': 0.0,
        'optional': 0.0
    }
    
    # Calculate mandatory fields completeness
    mandatory_fields = SAFETY_INFO_REQUIREMENTS['mandatory']
    mandatory_field_count = len(mandatory_fields)
    mandatory_present = sum(1 for field in mandatory_fields if field in product_data and product_data.get(field))
    category_scores['mandatory'] = mandatory_present / mandatory_field_count
    
    # Calculate recommended fields completeness
    recommended_fields = SAFETY_INFO_REQUIREMENTS['recommended']
    recommended_field_count = len(recommended_fields)
    if recommended_field_count > 0:
        recommended_present = sum(1 for field in recommended_fields if field in product_data and product_data.get(field))
        category_scores['recommended'] = recommended_present / recommended_field_count
    
    # Calculate optional fields completeness
    optional_fields = SAFETY_INFO_REQUIREMENTS['optional']
    optional_field_count = len(optional_fields)
    if optional_field_count > 0:
        optional_present = sum(1 for field in optional_fields if field in product_data and product_data.get(field))
        category_scores['optional'] = optional_present / optional_field_count
    
    # Calculate final weighted score
    final_score = (
        category_scores['mandatory'] * INFO_CATEGORY_WEIGHTS['mandatory'] +
        category_scores['recommended'] * INFO_CATEGORY_WEIGHTS['recommended'] +
        category_scores['optional'] * INFO_CATEGORY_WEIGHTS['optional']
    )
    
    # Scale to 0-100
    return round(final_score * 100, 1)


def assess_field_quality(field_name: str, field_value) -> float:
    """
    Assess the quality of information provided in a specific field.
    
    Args:
        field_name: Name of the field being assessed
        field_value: Value of the field
        
    Returns:
        Quality score between 0.0 and 1.0
    """
    if not field_value:
        return 0.0
        
    # Convert field value to string if it isn't already
    if not isinstance(field_value, str):
        # Handle special case for age_range which is a tuple
        if field_name == 'age_range' and isinstance(field_value, tuple) and len(field_value) == 2:
            # Check if both min and max ages are provided
            min_age, max_age = field_value
            if min_age is not None and max_age is not None:
                return 1.0
            elif min_age is not None or max_age is not None:
                return 0.5
            return 0.0
        
        # Convert other non-string values to string
        field_value = str(field_value)
    
    # Get criteria for this field
    criteria = FIELD_QUALITY_CRITERIA.get(field_name, {})
    if not criteria:
        # Basic length check if no specific criteria
        return min(1.0, len(field_value) / 50)
    
    # Calculate quality score based on criteria
    score = 0.0
    total_checks = 0
    
    # Check minimum length
    min_length = criteria.get('min_length', 0)
    if min_length > 0:
        total_checks += 1
        if len(field_value) >= min_length:
            score += 1.0
    
    # Check recommended length
    recommended_length = criteria.get('recommended_length', 0)
    if recommended_length > 0:
        total_checks += 1
        score += min(1.0, len(field_value) / recommended_length)
    
    # Check for required keywords
    keywords = criteria.get('contains_keywords', [])
    if keywords:
        total_checks += 1
        lowercase_value = field_value.lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in lowercase_value)
        score += min(1.0, matches / len(keywords))
    
    # Calculate average score
    return score / total_checks if total_checks > 0 else 0.0


def get_info_completeness_report(product_data: dict) -> dict:
    """
    Generate a comprehensive report on information completeness.
    
    Args:
        product_data: Dictionary containing product information fields
        
    Returns:
        Dictionary with detailed assessment and recommendations
    """
    if not product_data:
        return {
            "score": 0.0,
            "status": "missing",
            "message": "No product information provided",
            "fields": {},
            "recommendations": ["Provide basic product information"]
        }
    
    # Calculate overall score
    overall_score = calculate_info_score(product_data)
    
    # Determine status based on score
    if overall_score >= 90:
        status = "excellent"
    elif overall_score >= 75:
        status = "good"
    elif overall_score >= 50:
        status = "fair"
    elif overall_score >= 25:
        status = "poor"
    else:
        status = "critical"
    
    # Assess each field
    field_assessments = {}
    all_fields = []
    all_fields.extend(SAFETY_INFO_REQUIREMENTS['mandatory'])
    all_fields.extend(SAFETY_INFO_REQUIREMENTS['recommended'])
    all_fields.extend(SAFETY_INFO_REQUIREMENTS['optional'])
    
    for field in all_fields:
        # Determine which category this field belongs to
        if field in SAFETY_INFO_REQUIREMENTS['mandatory']:
            category = "mandatory"
        elif field in SAFETY_INFO_REQUIREMENTS['recommended']:
            category = "recommended"
        else:
            category = "optional"
        
        # Get field value
        value = product_data.get(field)
        present = field in product_data and value is not None
        
        # Assess quality if present
        quality_score = assess_field_quality(field, value) if present else 0.0
        
        field_assessments[field] = {
            "present": present,
            "category": category,
            "quality_score": quality_score,
            "description": INFO_FIELD_DESCRIPTIONS.get(field, ""),
            "value": value if present else None
        }
    
    # Generate recommendations
    recommendations = []
    
    # First address missing mandatory fields
    missing_mandatory = [
        field for field in SAFETY_INFO_REQUIREMENTS['mandatory'] 
        if not product_data.get(field)
    ]
    
    if missing_mandatory:
        recommendations.append(f"Add missing critical information: {', '.join(missing_mandatory)}")
    
    # Address low quality fields
    low_quality_fields = [
        field for field, assessment in field_assessments.items()
        if assessment['present'] and assessment['quality_score'] < 0.5
        and assessment['category'] in ['mandatory', 'recommended']
    ]
    
    if low_quality_fields:
        recommendations.append(f"Improve the quality of: {', '.join(low_quality_fields)}")
    
    # Recommended fields if score is decent but could be better
    if 50 <= overall_score < 80:
        missing_recommended = [
            field for field in SAFETY_INFO_REQUIREMENTS['recommended'] 
            if not product_data.get(field)
        ]
        if missing_recommended:
            recommendations.append(f"Consider adding: {', '.join(missing_recommended)}")
    
    # If score is already good, suggest optional fields
    if overall_score >= 80:
        missing_optional = [
            field for field in SAFETY_INFO_REQUIREMENTS['optional'] 
            if not product_data.get(field)
        ]
        if missing_optional:
            recommendations.append(f"For excellence, consider adding: {', '.join(missing_optional)}")
    
    return {
        "score": overall_score,
        "status": status,
        "message": f"Information completeness is {status.upper()}",
        "fields": field_assessments,
        "recommendations": recommendations
    }


def get_minimum_required_fields() -> list:
    """Return the list of minimum required fields for safety documentation."""
    return SAFETY_INFO_REQUIREMENTS['mandatory']
