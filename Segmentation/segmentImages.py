from ultralytics import YOLO
import cv2, torch, os, os.path, sys, math, shutil, gc
from PIL import Image, ImageOps
import numpy as np

Image.MAX_IMAGE_PIXELS = None

# Yolov8x Class Names:  {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'}

def get_segmentation_classes():
    while True:
        class_input = input("Enter the segmentation class numbers separated by commas (e.g., 0,2,5): ")
        try:
            classes = tuple(int(cls.strip()) for cls in class_input.split(','))
            return classes
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas.")

def maskImage(segmentationClasses, mask_prefix):
    for root, dirs, files in os.walk(image_dir):
        for f_img in files:
            if f_img.endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(root, f_img)
                
                try:
                    with Image.open(img_path) as image:
                        # Get original image dimensions
                        orig_width, orig_height = image.size
                        
                        results = model(image, conf=confidence)
                        for r in results:
                            # Create a single mask for all specified segmentation classes
                            mask = np.zeros((orig_height, orig_width), dtype=np.uint8)
                            
                            # Iterate through all detected objects
                            for i, (box, cls) in enumerate(zip(r.boxes.xyxy, r.boxes.cls)):
                                if int(cls) in segmentationClasses:
                                    if r.masks is not None:
                                        object_mask = r.masks.data[i].cpu().numpy()
                                        # Resize object_mask to match original image dimensions
                                        object_mask_resized = cv2.resize(object_mask, (orig_width, orig_height))
                                        # Combine masks using logical OR
                                        mask = np.logical_or(mask, object_mask_resized > 0.5).astype(np.uint8)
                            
                            # Only save the mask if objects were detected
                            if np.any(mask):
                                # Convert boolean mask to 0 and 255 values
                                mask = mask * 255
                                
                                # Save the combined mask with the user-defined prefix
                                mask_filename = f"{mask_prefix}{os.path.splitext(f_img)[0]}_mask.png"
                                mask_image = Image.fromarray(mask)
                                mask_image.save(os.path.join(output_dir, mask_filename))
                                
                                print(f"Mask saved for {img_path}")
                            else:
                                print(f"No objects detected in {img_path}")
                            
                except Exception as e:
                    print(f"Error processing {img_path}: {e}")

def get_valid_input(prompt, validator):
    while True:
        user_input = input(prompt)
        if validator(user_input):
            return user_input
        print("Invalid input. Please try again.")

def path_exists(path):
    return os.path.exists(path)

def load_model(model_path):
    try:
        return YOLO(model_path)
    except OSError as e:
        print(f"Error loading the model: {e}")
        print("Please check if the file path is correct and the file is not corrupted.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading the model: {e}")
        return None

# Get model path from user
while True:
    model_path = get_valid_input("Enter the path to the YOLO model: ", os.path.exists)
    model = load_model(model_path)
    if model is not None:
        break
    print("Failed to load the model. Please try again with a different path.")

# Get image directory from user
image_dir = get_valid_input("Enter the path to the image directory: ", os.path.exists)

# Get output directory from user
output_dir = get_valid_input("Enter the path for the output directory: ", lambda x: True)

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

imgSz = 1.0
confidence = 0.3
# Visdrone Seg classes
# segmentationClass = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
# Yolo8x Seg classes  (See classes at top)
segmentationClass = get_segmentation_classes()

# Print the selected segmentation classes
print(f"Selected segmentation classes: {segmentationClass}")

# Get confidence threshold from user
confidence = float(input("Enter the confidence threshold (0.0 to 1.0): "))

# Get mask filename prefix from user
mask_prefix = input("Enter the prefix for mask filenames (press Enter for no prefix): ")

maskImage(segmentationClass, mask_prefix)