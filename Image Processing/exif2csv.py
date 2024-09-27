# This script parses a directory of image exif metadata, sorts by CreationDate tag and computes exposure values from camera settings
# By Jeffrey Ian Wilson for the 3D Scanning Masterclass (www.jeffreyianwilson.com)


import csv
import math
import os

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

def run_exiftool_command(input_path, metadata_file):
    # Change directory to the input path
    os.chdir(input_path)

    # Build the exiftool command using proper path handling
    exiftool_command = (
        f'c:/Apps/exiftool -csv -r -ext dng -FileCreateDate -GPSPosition -Make -Model -ColorSpace -Megapixels '
        f'-imageWidth -imageHeight -LensModel -focalLength -focalLengthIn35mmFormat -HyperfocalDistance '
        f'-aperture -shutterSpeed -iso -WhiteBalance -ColorTemperature "{input_path}" > "{metadata_file}"'
    )

    os.system(exiftool_command)
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
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            sourcePath = os.path.join(input_path, row['SourceFile'])
            model = row['Model']
            try:
                aperture = float(row['Aperture'])
            except (ValueError, TypeError):
                print(f"Skipping row with invalid aperture: {row['Aperture']}")
                continue  # Skip this row if aperture is not valid
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

# Define variables
file_format = "dng"
input_path = r"D:/OneDrive/3D Scanning Masterclass/97 - Scan Capture and Processing/01 - Raw Data/"
metadata_file = r"D:/OneDrive/3D Scanning Masterclass/97 - Scan Capture and Processing/01 - Raw Data/metadata.csv"

# Read image exif data and write to csv file
run_exiftool_command(input_path, metadata_file)

# Compute exposure value based on metadata
compute_exposure_value(input_path, metadata_file)

