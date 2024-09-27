# This Agisoft Metashape Pro python script will automatically import masks for a multi-camera rig if subdirectory structure is the same.
# By Jeffrey Ian Wilson for the 3D Scanning Masterclass (www.jeffreyianwilson.com)

import Metashape
import os

def import_multi_camera_rig_masks():
    # Get the active document
    doc = Metashape.app.document

    # Check if a document is open
    if doc is None:
        print("No document is open. Please open a document and try again.")
        return

    # Get the active chunk
    chunk = doc.chunk

    # Check if a chunk is selected
    if chunk is None:
        print("No chunk is selected. Please select a chunk and try again.")
        return

    # Prompt user for the root mask directory
    root_mask_dir = Metashape.app.getExistingDirectory("Select root folder containing mask images")
    if not root_mask_dir:
        print("Root mask directory not selected. Exiting.")
        return

    # Function to find mask file in directory structure
    def find_mask_file(root_dir, camera_label):
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff')) and camera_label.lower() in file.lower():
                    return os.path.join(root, file)
        return None

    # Get total number of cameras for progress calculation
    total_cameras = len(chunk.cameras)

    # Iterate through cameras in the chunk
    for i, camera in enumerate(chunk.cameras):
        # Update progress
        progress = (i + 1) / total_cameras
        print(f"Progress: {progress:.1%}")

        # Find the mask file for the camera
        mask_path = find_mask_file(root_mask_dir, camera.label)

        if mask_path:
            # Create a Mask object and load the image
            mask = Metashape.Mask()
            try:
                mask.load(mask_path)
                # Assign the mask to the camera
                camera.mask = mask
                print(f"Imported mask for camera: {camera.label}")
            except RuntimeError as e:
                print(f"Error loading mask for camera {camera.label}: {str(e)}")
        else:
            print(f"Mask not found for camera: {camera.label}")

        # Update Metashape UI
        Metashape.app.update()

    print("Mask import complete.")

# Run the script
import_multi_camera_rig_masks()
