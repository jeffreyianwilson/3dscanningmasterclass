# This script parses a directory of image exif metadata, sorts by CreationDate tag and computes exposure values from camera settings
# By Jeffrey Ian Wilson for the 3D Scanning Masterclass (www.jeffreyianwilson.com)

import csv
import math
import os
import subprocess

def sort_csv_by_create_date(csv_file):
    # Read the CSV content
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Extract the header
        rows = list(reader)    # Extract the rest of the rows

    # Sort rows by CreateDate (2nd column, index 1)
    rows.sort(key=lambda x: x[1])  # Assuming CreateDate is at index 1

    # Write the sorted content back to the CSV file
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Write the header
        writer.writerows(rows)   # Write sorted rows

def run_exiftool_command(input_path, metadata_file, ignore_folder):
    # Change directory to the input path
    os.chdir(input_path)

    # Build the exiftool command
    exiftool_command = [
        'c:/Apps/exiftool', '-csv', '-r', '-ext', 'dng',
        '-FileCreateDate', '-GPSPosition', '-Make', '-Model', '-ColorSpace', '-Megapixels',
        '-imageWidth', '-imageHeight', '-LensModel', '-focalLength', '-focalLengthIn35mmFormat', '-HyperfocalDistance',
        '-aperture', '-shutterSpeed', '-iso', '-WhiteBalance', '-ColorTemperature',
        input_path
    ]

    # Run exiftool and capture its output
    result = subprocess.run(exiftool_command, capture_output=True, text=True)
    
    # Process the output
    lines = result.stdout.split('\n')
    header = lines[0]
    filtered_lines = [header]  # Start with the header

    for line in lines[1:]:
        if line.strip() and ignore_folder not in line:
            filtered_lines.append(line)
        elif ignore_folder in line:
            print(f"Skipping file: {line.split(',')[0]} (contains ignore folder)")

    # Write the filtered output to the metadata file
    with open(metadata_file, 'w', newline='') as f:
        f.write('\n'.join(filtered_lines))

    sort_csv_by_create_date(metadata_file)

def remove_characters_from_csv(csv_file, characters_to_remove):
    with open(csv_file, 'r') as file:
        csv_content = file.read()

    for char in characters_to_remove:
        csv_content = csv_content.replace(char, '')

    with open(csv_file, 'w') as file:
        file.write(csv_content)

def compute_exposure_value(input_path, metadata_file):
    temp_file = "temp_metadata.csv"

    with open(metadata_file, 'r') as infile, open(temp_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['ExposureValue']
        if 'Aperture' not in fieldnames:
            fieldnames.append('Aperture')
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            sourcePath = os.path.join(input_path, row['SourceFile'])
            model = row['Model']
            
            if 'Aperture' not in row or not row['Aperture']:
                print(f"Aperture not found for {row['SourceFile']}. Using default value of {default_aperture}")
                row['Aperture'] = str(default_aperture)
            
            try:
                aperture = float(row['Aperture'])
            except ValueError:
                print(f"Invalid aperture value for {row['SourceFile']}. Using default value of {default_aperture}")
                aperture = default_aperture
            
            shutter_speed = row['ShutterSpeed']
            numerator, denominator = map(float, shutter_speed.split('/'))
            shutter_speed = numerator / denominator
            iso = float(row['ISO'])

            # Add path to SourceFile
            row['SourceFile'] = sourcePath

            # Write exposure value
            row['ExposureValue'] = f"{math.log2((aperture**2) / shutter_speed) + math.log2(iso/100):.2f}"
            writer.writerow(row)

    os.replace(temp_file, metadata_file)

def remove_duplicates(csv_file):
    temp_file = "temp_no_duplicates.csv"
    
    with open(csv_file, 'r') as infile, open(temp_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        seen = set()
        for row in reader:
            row_tuple = tuple(row)
            if row_tuple not in seen:
                seen.add(row_tuple)
                writer.writerow(row)
            else:
                print(f"Duplicate row found and removed: {row}")
    
    os.replace(temp_file, csv_file)
    print(f"Duplicates removed. Unique rows: {len(seen)}")

# Define variables
file_format = "dng"
input_path = r"D:\OneDrive\3D Scanning Masterclass\97 - Scan Capture and Processing\01 - Raw Data\2024-09-21\Navvis MLX"
metadata_file = r"D:/OneDrive/3D Scanning Masterclass/97 - Scan Capture and Processing/01 - Raw Data/metadata_navvisMLX.csv"
default_aperture = 2.0
remove_duplicates_flag = True  # Set this to False if you don't want to remove duplicates
ignore_folder = "camCC"  # Folder name to ignore when processing images

# Read image exif data and write to csv file
run_exiftool_command(input_path, metadata_file, ignore_folder)

# Compute exposure value based on metadata
compute_exposure_value(input_path, metadata_file)

# Remove duplicates if the flag is set to True
if remove_duplicates_flag:
    remove_duplicates(metadata_file)
