# This python script uses Raw Therapee CLI commands to read a raw therapee pp3 file then adjust white balance and adjust exposure to a defined EV value with an exposure offset
# By Jeffrey Ian Wilson for the 3D Scanning Masterclass (www.jeffreyianwilson.com)

import exifread, math, fractions, os

def get_camera_ev(input_image):
    with open(input_image, 'rb') as f:
        tags = exifread.process_file(f)
        aperture = float(fractions.Fraction(str(tags['EXIF FNumber'])))
        shutter_speed = float(fractions.Fraction(str(tags['EXIF ExposureTime'])))
        iso = float(tags['EXIF ISOSpeedRatings'].values[0])  # Assuming ISO is a simple integer value
        camera_ev = f"{math.log2((aperture**2) / shutter_speed) + math.log2(iso/100):.2f}"
        return camera_ev

def update_pp3_file(pp3_file, variables_to_change):
    variables = {}
    all_lines = []

    with open(pp3_file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        all_lines.append(line)
        if '[' in line and ']' in line:
            continue
        if '=' in line:
            var, val = line.strip().split('=', 1)
            try:
                val = int(val)
            except ValueError:
                pass
            variables[var] = val

    for var, new_val in variables_to_change.items():
        if var in variables:
            variables[var] = new_val

    for i, line in enumerate(all_lines):
        for var in variables_to_change:
            if var + '=' in line:
                prefix, rest = line.split('=', 1)
                all_lines[i] = prefix + '=' + str(variables[var]) + '\n'

    with open(pp3_file, 'w') as f:
        f.writelines(all_lines)

# Path to the directory of images
image_path_input = "D:\\"
image_path_output = "D:\\"
pp3_file = "D:\\file.pp3"
temperature = 5500
new_camera_ev = 13.5
exposure_offset = 0.0
adjust_exposure = True

# Iterate over each file in the directory
for filename in os.listdir(image_path_input):
    if filename.endswith(".dng"):  # Assuming we're only interested in .dng files
        input_image = os.path.join(image_path_input, filename)
        output_image = os.path.join(image_path_output, filename.replace('.dng', '.jpg'))

        if adjust_exposure:
            compensation = round(float(get_camera_ev(input_image)) - new_camera_ev, 2) + exposure_offset
            variables_to_change = {'Temperature': temperature, 'Compensation': compensation}
        else:
            variables_to_change = {'Temperature': temperature}

        print(f"Processing file: {filename}")
        if adjust_exposure:
            print(f"Camera EV: {get_camera_ev(input_image)}")  
            print(f"New Camera EV: {new_camera_ev}")
            print(f"Exposure Offset: {compensation}")

        update_pp3_file(pp3_file, variables_to_change)

        rawtherapee_cli_path = "\"C:\\Program Files\\RawTherapee\\5.9\\rawtherapee-cli.exe\""
        command = f"{rawtherapee_cli_path} -Y -o {output_image} -p {pp3_file} -c {input_image}"
        os.system(command)
