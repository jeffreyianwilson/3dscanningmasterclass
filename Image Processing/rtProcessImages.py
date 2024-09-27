# This python script uses Raw Therapee CLI commands to read a raw therapee pp3 file then adjust white balance and adjust exposure to a defined EV value with an exposure offset
# By Jeffrey Ian Wilson for the 3D Scanning Masterclass (www.jeffreyianwilson.com)

# Please note, this script is a work in progress and has a few bugs.

import exifread, math, fractions, os

def get_camera_ev(input_image):
    with open(input_image, 'rb') as f:
        tags = exifread.process_file(f)
        
        # Set default aperture to 2.0
        aperture = 2.0
        
        # Try to get FNumber, use default if not found
        if 'EXIF FNumber' in tags:
            try:
                aperture = float(fractions.Fraction(str(tags['EXIF FNumber'])))
            except (ValueError, ZeroDivisionError):
                print(f"Warning: Invalid FNumber for {input_image}, using default aperture of 2.0")
        else:
            print(f"Warning: FNumber not found for {input_image}, using default aperture of 2.0")
        
        shutter_speed = float(fractions.Fraction(str(tags['EXIF ExposureTime'])))
        iso = float(tags['EXIF ISOSpeedRatings'].values[0])  # Assuming ISO is a simple integer value
        camera_ev = f"{math.log2((aperture**2) / shutter_speed) + math.log2(iso/100):.2f}"
        return camera_ev

def update_pp3_file(pp3_file, variables_to_change):
    all_lines = []
    current_section = None

    with open(pp3_file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if line.strip().startswith('['):
            current_section = line.strip()[1:-1]
        
        if current_section == 'White Balance':
            for var, new_val in variables_to_change.items():
                if var in line:
                    line = f"{var}={new_val}\n"
                    break
        elif current_section == 'Exposure':
            if 'Compensation' in variables_to_change and 'Compensation=' in line:
                line = f"Compensation={variables_to_change['Compensation']}\n"
        
        all_lines.append(line)

    with open(pp3_file, 'w') as f:
        f.writelines(all_lines)

# Path to the directory of images
image_path_input = "D:\\OneDrive\\3D Scanning Masterclass\\97 - Scan Capture and Processing\\01 - Raw Data\\2024-09-21\\Navvis VLX3\\2024-09-21_19.09.20\\camCC"
image_path_output = "D:\\OneDrive\\3D Scanning Masterclass\\97 - Scan Capture and Processing\\02 - Source Data\\2024-09-21\\Navvis VLX3\\01_ev14.5"
pp3_file = "D:\\OneDrive\\3D Scanning Masterclass\\97 - Scan Capture and Processing\\01 - Raw Data\\Color Calibration\\navvisVLX.pp3"
temperature = 5500
new_camera_ev = 14.5
base_ev = 0  # Reference point for EV adjustment
exposure_offset = 0.0
adjust_exposure = True
navvis_image = True

# Iterate over each file in the directory
for filename in os.listdir(image_path_input):
    if filename.endswith(".dng"):  # Assuming we're only interested in .dng files
        input_image = os.path.join(image_path_input, filename)
        output_image = os.path.join(image_path_output, filename.replace('.dng', '.jpg'))
        
        # Create a new pp3 file for each input image
        new_pp3_file = os.path.join(image_path_input, filename + ".pp3")

        if adjust_exposure:
            camera_ev = float(get_camera_ev(input_image))
            # Correct the compensation calculation
            compensation = round(new_camera_ev - camera_ev, 2) + exposure_offset
            variables_to_change = {'Temperature': temperature, 'Compensation': compensation}
        else:
            variables_to_change = {'Temperature': temperature}

        print(f"Processing file: {filename}")
        if adjust_exposure:
            print(f"Camera EV: {camera_ev}")  
            print(f"Target EV: {new_camera_ev}")
            print(f"Exposure Compensation: {compensation}")

        # Copy the original pp3 file to the new one and update it
        import shutil
        shutil.copy2(pp3_file, new_pp3_file)
        update_pp3_file(new_pp3_file, variables_to_change)

        # Use subprocess.run instead of os.system, and quote the paths
        import subprocess
        command = [
            r"C:\Program Files\RawTherapee\5.10\rawtherapee-cli.exe",
            "-Y",
            "-o", output_image,
            "-p", new_pp3_file,
            "-c", input_image
        ]
        subprocess.run(command, check=True)

import os
import re
import shutil

def sort_navvis_images(image_path_output):
    # Ensure the source directory exists
    if not os.path.exists(image_path_output):
        print(f"Error: Source directory does not exist.")
        return

    # Regular expression to match "cam#" in filenames
    cam_pattern = re.compile(r'cam(\d+)')

    # Iterate through all files in the source directory
    for filename in os.listdir(image_path_output):
        file_path = os.path.join(image_path_output, filename)
        
        # Check if it's a file (not a directory)
        if os.path.isfile(file_path):
            # Search for "cam#" in the filename
            match = cam_pattern.search(filename)
            
            if match:
                cam_number = match.group(1)
                target_dir = os.path.join(image_path_output, f"cam{cam_number}")
                
                # Create the target directory if it doesn't exist
                os.makedirs(target_dir, exist_ok=True)
                
                # Move the file to the target directory
                target_path = os.path.join(target_dir, filename)
                shutil.move(file_path, target_path)
                print(f"Moved '{filename}' to '{target_dir}'")
        # Optionally, remove the temporary pp3 file after processing

if navvis_image:
    sort_navvis_images(image_path_output)    #os.remove(new_pp3_file)
