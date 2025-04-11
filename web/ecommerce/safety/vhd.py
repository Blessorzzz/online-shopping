"""
Visual Hazard Detection (VHD) Module
------------------------------------
This module handles all calculations and data related to the Visual Hazard Detection (VHD),
which analyzes product images for potential safety hazards.
"""

from django.conf import settings
import os

# Hazard detection thresholds and configuration
HAZARD_DETECTION_CONFIG = {
    'small_part': {
        'max_size': 3.5,  # cm
        'min_confidence': 0.7,
        'description': 'Parts small enough to be swallowed or aspirated',
        'severity': 'high'
    },
    'sharp_edge': {
        'min_angle': 60,  # degrees
        'edge_length': 2.0,  # cm
        'min_confidence': 0.6,
        'description': 'Edges that could cut or puncture skin',
        'severity': 'high'
    },
    'point': {
        'min_sharpness': 0.5,  # radius in mm
        'min_confidence': 0.65,
        'description': 'Sharp points that could puncture skin',
        'severity': 'high'
    },
    'long_cord': {
        'min_length': 15.0,  # cm
        'min_confidence': 0.75,
        'description': 'Cords that pose strangulation hazard',
        'severity': 'high'
    },
    'projectile': {
        'min_velocity': 2.0,  # m/s
        'min_confidence': 0.7,
        'description': 'Items that can be launched/propelled',
        'severity': 'medium'
    },
    'magnet': {
        'min_strength': 0.3,  # Tesla
        'min_confidence': 0.6,
        'description': 'Magnets that could be swallowed and cause internal injuries',
        'severity': 'high'
    },
    'battery': {
        'types': ['button', 'coin', 'cylindrical'],
        'min_confidence': 0.8,
        'description': 'Batteries accessible to children',
        'severity': 'high'
    },
    'toxic_color': {
        'color_range': [(0, 50, 50), (70, 255, 255)],  # HSV range for suspicious colors
        'min_confidence': 0.5,
        'description': 'Colors suggesting potentially harmful chemicals',
        'severity': 'medium'
    }
}

# Hazard category explanations
HAZARD_CATEGORIES = {
    'mechanical': {
        'name': 'Mechanical Hazards',
        'description': 'Physical dangers like sharp edges, small parts, or pinch points',
        'examples': ['small_part', 'sharp_edge', 'point', 'projectile']
    },
    'strangulation': {
        'name': 'Strangulation Hazards',
        'description': 'Items that can wrap around a child\'s neck',
        'examples': ['long_cord', 'drawstring', 'loop']
    },
    'choking': {
        'name': 'Choking Hazards',
        'description': 'Items that can block airway if ingested',
        'examples': ['small_part', 'magnet', 'battery', 'marble']
    },
    'chemical': {
        'name': 'Chemical Hazards',
        'description': 'Toxic substances that can cause poisoning if ingested or absorbed',
        'examples': ['toxic_color', 'lead_paint', 'phthalates']
    },
    'suffocation': {
        'name': 'Suffocation Hazards',
        'description': 'Items that can block breathing or cause asphyxiation',
        'examples': ['plastic_bag', 'packaging_film']
    }
}


class VisualSafetyInspector:
    """
    Class for analyzing product images to detect potential safety hazards.
    """
    def __init__(self):
        self.hazard_rules = HAZARD_DETECTION_CONFIG
        self.mock_mode = True  # For demonstration without actual CV implementation
    
    def analyze_image(self, img_path: str) -> dict:
        """
        Analyze a product image for potential safety hazards.
        
        Parameters:
        - img_path: Path to the image file
        
        Returns:
        - Dictionary containing detected hazards and measurements
        """
        results = {'hazards': [], 'measurements': {}}
        
        # Check if file exists
        if not os.path.exists(img_path):
            results['error'] = f"Image file not found: {img_path}"
            return results
        
        # In mock mode, generate demo results based on filename
        if self.mock_mode:
            return self._generate_mock_results(img_path)
            
        # In actual implementation, this would use OpenCV, TensorFlow, etc.
        # to analyze the image and detect potential hazards
        
        # Placeholder for future computer vision implementation
        
        return results
    
    def _generate_mock_results(self, img_path: str) -> dict:
        """
        Generate mock hazard detection results based on filename for demonstration.
        This would be replaced by actual computer vision in production.
        """
        results = {'hazards': [], 'measurements': {}}
        
        # Mock logic - detect "hazards" based on filename
        filename = os.path.basename(img_path).lower()
        
        if 'small' in filename or 'part' in filename:
            results['hazards'].append({
                'type': 'small_part',
                'confidence': 0.85,
                'location': {'x': 120, 'y': 150, 'width': 30, 'height': 25},
                'measurements': {'diameter': 2.1}
            })
            results['measurements']['smallest_part_diameter'] = 2.1
        
        if 'sharp' in filename or 'edge' in filename:
            results['hazards'].append({
                'type': 'sharp_edge',
                'confidence': 0.78,
                'location': {'x': 200, 'y': 180, 'width': 40, 'height': 5},
                'measurements': {'angle': 65, 'length': 3.5}
            })
            results['measurements']['sharpest_edge_angle'] = 65
        
        if 'cord' in filename or 'string' in filename:
            results['hazards'].append({
                'type': 'long_cord',
                'confidence': 0.92,
                'location': {'x': 100, 'y': 200, 'width': 300, 'height': 10},
                'measurements': {'length': 30.5}
            })
            results['measurements']['longest_cord_length'] = 30.5
        
        if 'battery' in filename:
            results['hazards'].append({
                'type': 'battery',
                'confidence': 0.88,
                'location': {'x': 150, 'y': 120, 'width': 20, 'height': 20},
                'measurements': {'diameter': 1.8, 'type': 'button'}
            })
        
        # Add basic measurements for all images
        results['measurements']['overall_dimensions'] = {
            'width': 20.5,
            'height': 15.2,
            'depth': 8.7
        }
        
        return results


def calculate_vhd_score(detected_hazards: list) -> float:
    """
    Calculate Visual Hazard Detection score based on detected hazards.
    
    Parameters:
    - detected_hazards: List of hazards detected in the product
    
    Returns:
    - Score from 0-100 (higher is better/safer)
    """
    if not detected_hazards:
        return 100  # No hazards detected = perfect score
    
    # Base deduction for each hazard based on severity
    severity_weights = {
        'high': 20,
        'medium': 10,
        'low': 5
    }
    
    total_deduction = 0
    
    for hazard in detected_hazards:
        # Handle both string hazards and dictionary hazards
        if isinstance(hazard, str):
            hazard_type = hazard
            confidence = 1.0  # Default confidence if not specified
        elif isinstance(hazard, dict) and 'type' in hazard:
            hazard_type = hazard['type']
            confidence = hazard.get('confidence', 1.0)
        else:
            continue
        
        # Get hazard config
        hazard_config = HAZARD_DETECTION_CONFIG.get(hazard_type)
        if hazard_config:
            severity = hazard_config.get('severity', 'medium')
            # Weight the deduction by confidence level
            total_deduction += severity_weights.get(severity, 10) * confidence
    
    # Ensure score is within 0-100 range
    score = max(0, min(100, 100 - total_deduction))
    return score


def get_hazard_categories(detected_hazards: list) -> dict:
    """
    Group detected hazards by category for reporting.
    
    Parameters:
    - detected_hazards: List of hazards detected in the product
    
    Returns:
    - Dictionary of categorized hazards
    """
    categorized = {
        'mechanical': [],
        'strangulation': [],
        'choking': [],
        'chemical': [],
        'suffocation': [],
        'other': []
    }
    
    for hazard in detected_hazards:
        # Extract hazard type
        if isinstance(hazard, str):
            hazard_type = hazard
        elif isinstance(hazard, dict) and 'type' in hazard:
            hazard_type = hazard['type']
        else:
            continue
        
        # Find which category this hazard belongs to
        assigned = False
        for category, info in HAZARD_CATEGORIES.items():
            if hazard_type in info['examples']:
                categorized[category].append(hazard)
                assigned = True
                break
        
        # If not assigned to any category, put in "other"
        if not assigned:
            categorized['other'].append(hazard)
    
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}


def get_vhd_report(product) -> dict:
    """
    Generate a comprehensive visual hazard detection report for a product.
    
    Parameters:
    - product: Product object with image and safety issue information
    
    Returns:
    - Dictionary containing visual hazard analysis
    """
    if hasattr(product, 'product_type') and product.product_type != 'tangible':
        return {
            "applicable": False,
            "message": "Visual hazard detection not applicable for virtual products"
        }
    
    # Get product details and image path
    if hasattr(product, 'thumbnail_image') and product.thumbnail_image:
        try:
            img_path = product.thumbnail_image.path
        except Exception:
            img_path = None
    else:
        img_path = None
    
    detected_hazards = product.safety_issues if hasattr(product, 'safety_issues') else []
    
    # Analyze image if available
    image_results = {}
    analyzed_hazards = []
    if img_path:
        inspector = VisualSafetyInspector()
        image_results = inspector.analyze_image(img_path)
        if 'hazards' in image_results:
            analyzed_hazards = image_results['hazards']
    
    # Combine manually entered and detected hazards
    combined_hazards = detected_hazards.copy()
    for hazard in analyzed_hazards:
        if isinstance(hazard, dict) and 'type' in hazard:
            hazard_type = hazard['type']
            # Check if this hazard type already exists
            existing = False
            for h in combined_hazards:
                if (isinstance(h, str) and h == hazard_type) or \
                   (isinstance(h, dict) and 'type' in h and h['type'] == hazard_type):
                    existing = True
                    break
            if not existing:
                combined_hazards.append(hazard)
    
    # Calculate VHD score
    vhd_score = calculate_vhd_score(combined_hazards)
    
    # Categorize hazards
    categorized_hazards = get_hazard_categories(combined_hazards)
    
    # Generate recommendations based on hazards
    recommendations = []
    if vhd_score < 80:
        recommendations.append("Product has significant safety concerns detected visually")
    
    if 'mechanical' in categorized_hazards and len(categorized_hazards['mechanical']) > 0:
        recommendations.append("Address mechanical hazards through improved design or warnings")
    
    if 'strangulation' in categorized_hazards:
        recommendations.append("Ensure all cords and strings comply with industry standards")
    
    if 'choking' in categorized_hazards:
        recommendations.append("Include clear choking hazard warnings and age recommendations")
    
    # Add specific recommendations for each major hazard
    for hazard in combined_hazards:
        hazard_type = hazard['type'] if isinstance(hazard, dict) and 'type' in hazard else hazard
        config = HAZARD_DETECTION_CONFIG.get(hazard_type)
        if config and config.get('severity') == 'high':
            recommendations.append(f"Address '{hazard_type}' hazard: {config.get('description')}")
    
    return {
        "applicable": True,
        "score": vhd_score,
        "analyzed_image": bool(img_path),
        "image_path": img_path,
        "detected_hazards": analyzed_hazards,
        "manual_hazards": detected_hazards,
        "combined_hazards": combined_hazards,
        "hazard_categories": categorized_hazards,
        "measurements": image_results.get('measurements', {}),
        "recommendations": recommendations
    }
