import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from ecommerce.models import Product

class EdgeSharpnessAnalyzer:
    def __init__(self, sharp_threshold=0.15, curvature_threshold=1000):
        """Initialize the edge detection analyzer."""
        self.sharp_threshold = sharp_threshold
        self.curvature_threshold = curvature_threshold

    def analyze_image(self, image_path, product_id=None, visualize=True):
        """Analyze the sharpness of the given image and store safety warning in the product's safety_issues field."""
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image {image_path} not found")

        # Preprocessing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Edge detection using Canny
        edges = cv2.Canny(blurred, 50, 150)

        # Calculate sharpness
        sharpness = np.mean(edges) / 255.0
        is_sharp = sharpness > self.sharp_threshold

        # Detect sharp corners (using convexity defects)
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        sharp_corners = 0
        for cnt in contours:
            if len(cnt) < 3:
                continue

            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
            if len(approx) >= 3:
                hull = cv2.convexHull(approx, returnPoints=False)
                if hull is not None and len(hull) >= 3:
                    try:
                        defects = cv2.convexityDefects(approx, hull)
                        if defects is not None:
                            for i in range(defects.shape[0]):
                                _, _, _, d = defects[i, 0]
                                if d > self.curvature_threshold:
                                    sharp_corners += 1
                                    break
                    except cv2.error as e:
                        print(f"Skipping contour due to error: {e}")
                        continue

                # Safety warning
        safety_warning = "sharp_edges" if (is_sharp or sharp_corners > 0) else None

        # If product_id is provided, update the product's safety_issues field
        if product_id and safety_warning:
            try:
                product = Product.objects.get(product_id=product_id)
                print(f"Found product: {product.product_name}")
                print(f"Current safety issues (before): {product.safety_issues}")
                print(f"Type of safety_issues: {type(product.safety_issues)}")

                # Force initialize as a Python list
                safety_issues = []
                if product.safety_issues:
                    # Try to handle various possible states
                    if isinstance(product.safety_issues, list):
                        safety_issues = product.safety_issues
                    elif isinstance(product.safety_issues, str):
                        # Handle case where it might be a JSON string
                        try:
                            import json
                            safety_issues = json.loads(product.safety_issues)
                            if not isinstance(safety_issues, list):
                                safety_issues = []
                        except:
                            safety_issues = []
                
                # Add the new warning if not already present
                if safety_warning not in safety_issues:
                    safety_issues.append(safety_warning)
                    
                    # Explicitly set the field
                    product.safety_issues = safety_issues
                    
                    # Force save and commit
                    product.save(update_fields=['safety_issues'])
                    
                    # Verify the save worked by re-querying from DB
                    refreshed_product = Product.objects.get(product_id=product_id)
                    print(f"Updated safety issues (after save): {refreshed_product.safety_issues}")
                    print(f"Type after save: {type(refreshed_product.safety_issues)}")
                else:
                    print(f"Safety warning '{safety_warning}' already exists in product safety issues.")
            except Product.DoesNotExist:
                print(f"Product with ID {product_id} not found.")
            except Exception as e:
                print(f"Error updating safety issues: {str(e)}")
                import traceback
                traceback.print_exc()

        # Visualization
        if visualize:
            self._save_visualization(image, edges, image_path, sharpness, sharp_corners)

        return {
            "image_path": image_path,
            "sharpness_score": round(sharpness, 3),
            "is_sharp": is_sharp,
            "sharp_corners": sharp_corners,
            "safety_warning": safety_warning
        }

    def _save_visualization(self, image, edges, image_path, sharpness, sharp_corners):
        """Save the visualization results."""
        plt.figure(figsize=(12, 6))

        # Original image
        plt.subplot(1, 2, 1)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.title("Original Image")
        plt.axis('off')

        # Edge detection result
        plt.subplot(1, 2, 2)
        plt.imshow(edges, cmap='gray')
        plt.title(f"Edge Analysis\nSharpness: {sharpness:.2f}, Sharp Corners: {sharp_corners}")
        plt.axis('off')

        # Save the output
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, os.path.basename(image_path))
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(f"Visualization saved at: {output_path}")


if __name__ == "__main__":
    # Create the analyzer object with the desired thresholds
    analyzer = EdgeSharpnessAnalyzer(sharp_threshold=0.15, curvature_threshold=1000)

    # Directory containing the images
    image_dir = "images"

    # Loop through all the files in the images directory
    for img_name in os.listdir(image_dir):
        img_path = os.path.join(image_dir, img_name)
        
        # Check if it's an image file (you can refine this to check for specific formats)
        if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"\nProcessing image: {img_name}")
            result = analyzer.analyze_image(img_path)
            print("\nDetection results:")
            for k, v in result.items():
                print(f"{k:15}: {v}")
