import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from ecommerce.models import Product

class EdgeSharpnessAnalyzer:
    def __init__(self, sharp_threshold=0.1, curvature_threshold=800):
        """Initialize the edge detection analyzer."""
        self.sharp_threshold = sharp_threshold  # Lowered to increase sensitivity
        self.curvature_threshold = curvature_threshold  # Lowered to detect more sharp corners

    def analyze_image(self, image_path, product_id=None, visualize=True):
        """Analyze the sharpness of the given image and store safety warning in the product's safety_issues field."""
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image {image_path} not found")

        # Preprocessing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)  # Reduced kernel size for finer edge detection

        # Edge detection using Canny
        edges = cv2.Canny(blurred, 30, 100)  # Lowered thresholds for more edge sensitivity

        # Calculate sharpness
        sharpness = np.mean(edges) / 255.0
        
        # Classify sharpness into VHD score categories with refined thresholds
        if sharpness <= 0.04:  # Adjusted threshold for "Dull"
            sharpness_category = "Dull"
            vhd_score = 1  # Lowest hazard score for dull objects
        elif sharpness <= 0.08:  # Adjusted threshold for "Medium"
            sharpness_category = "Medium"
            vhd_score = 3  # Medium hazard score
        else:  # Anything above 0.08 is considered "Sharp"
            sharpness_category = "Sharp"
            vhd_score = 5  # Highest hazard score for sharp objects
        
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

        # Safety warning: Only generate "sharp_edges" if the category is "Sharp"
        safety_warning = "sharp_edges" if sharpness_category == "Sharp" else None

        # If product_id is provided, update the product's safety_issues and vhd_score fields
        if product_id:
            try:
                product = Product.objects.get(product_id=product_id)
                if safety_warning:
                    # Update safety issues
                    if not product.safety_issues:
                        product.safety_issues = []
                    if safety_warning not in product.safety_issues:
                        product.safety_issues.append(safety_warning)
                
                # Update VHD score
                product.vhd_score = vhd_score
                product.sharpness_category = sharpness_category

                # Print the category, relative category score, and safety warning in the terminal
                print(f"Category: {sharpness_category}")
                print(f"Relative Category Score: {vhd_score}")
                print(f"Safety Warning for {product.product_name}: {safety_warning}")

                product.save()
            except Exception as e:
                print(f"Failed to update product safety information: {e}")
                pass

        # Visualization - modified to hide sharp corners details
        if visualize:
            self._save_visualization(image, edges, image_path, sharpness, sharpness_category)

        return {
            "image_path": image_path,
            "sharpness_score": round(sharpness, 3),
            "sharpness_category": sharpness_category,
            "vhd_score": vhd_score,
            "is_sharp": is_sharp,
            "safety_warning": safety_warning
        }

    def _save_visualization(self, image, edges, image_path, sharpness, sharpness_category):
        """Save the visualization results without showing sharp corners."""
        plt.figure(figsize=(12, 6))

        # Original image
        plt.subplot(1, 2, 1)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.title("Original Image")
        plt.axis('off')

        # Edge detection result - modified to hide sharp corners info
        plt.subplot(1, 2, 2)
        plt.imshow(edges, cmap='gray')
        plt.title(f"Edge Analysis\nSharpness: {sharpness:.2f}\nCategory: {sharpness_category}")
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
    analyzer = EdgeSharpnessAnalyzer(sharp_threshold=0.1, curvature_threshold=800)

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