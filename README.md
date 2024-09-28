# 3D Scanning Masterclass
A collection of sample data, trained computer vision models and various python scripts for processing data for the 3D Scanning Masterclass.

<b>Image Processing/exif2csv.py</b><br>
Python script to parse image exif metadata and compute exposure values into a CSV file.<br><br>
<b>Image Processing/rtProcessImages.py</b><br>
Python script using Raw Therapee CLI commands to read a raw therapee pp3 file then adjust white balance and adjust exposure to a defined EV value with an exposure offset.<br><br>
<b>Metashape/alignOptimizeCameras.py</b><br>
This Agisoft Metashape Pro python script will automatically align, filter tie points and optimize cameras.<br><br>
<b>Metashape/importMultiCameraRigMasks.py</b><br>
This Agisoft Metashape Pro python script will automatically import masks on selected images for a multi-camera rig if subdirectory structure is the same.<br><br>
<b>Segmentation/segmentImages.py</b><br>
Python script to detect and mask objects using a trained Yolo segmentation model.<br><br>
