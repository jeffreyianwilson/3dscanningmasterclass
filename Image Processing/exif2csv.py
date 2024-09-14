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

def run_exiftool_command(input_path):
    os.chdir(input_path)
    exiftool_command = (
        "c:/Apps/exiftool -csv -CreateDate -GPSPosition -Make -Model -ColorSpace -Megapixels -imageWidth -imageHeight "
        "-LensModel -focalLength -focalLengthIn35mmFormat -HyperfocalDistance -aperture -shutterSpeed "
        "-iso -WhiteBalance -ColorTemperature *.* > " + metadata_file
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

def compute_exposure_value(metadata_file):
    temp_file = "temp_metadata.csv"

    with open(metadata_file, 'r') as infile, open(temp_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['ExposureValue']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            sourcePath = input_path + row['SourceFile']
            model = row['Model']
            try:
                aperture = float(row['Aperture'])
            except (ValueError, TypeError):
                print(f"Skipping row with invalid aperture: {row['Aperture']}")
                continue  # Skip this row if aperture is not valid
            shutter_speed = row['ShutterSpeed']
            numerator, denominator = map(float, shutter_speed.split('/'))
            shutter_speed = float(numerator)/float(denominator)
            iso = float(row['ISO'])

            # Add path to SourceFile
            row['SourceFile'] = sourcePath

            # Write exposure value
            row['ExposureValue'] = f"{math.log2((aperture**2) / shutter_speed) + math.log2(iso/100):.2f}"
            writer.writerow(row)

    os.replace(temp_file, metadata_file)


# Define variables
input_path = "D:/temp/"
csv_path = "D:/temp/"
metadata_file = os.path.join(csv_path, "metadata.csv")

# Read image exif data and write to csv file
run_exiftool_command(input_path)

# Characters to remove from the CSV file
#characters_to_remove = [' ', 'mm', '+', "f/"]
#remove_characters_from_csv(metadata_file, characters_to_remove)

# Pass metadata_file as an argument to compute exposure
compute_exposure_value(metadata_file)
