import Metashape
import sys

doc = Metashape.app.document
chunk = doc.chunk

AlignCameras = True
ResetMatches = True
if AlignCameras == True:
    # Align Cameras
    chunk.matchPhotos(downscale = 1, reset_matches = ResetMatches, filter_mask = True, keypoint_limit = 80000, tiepoint_limit = 20000, generic_preselection = True, reference_preselection = True)
    chunk.alignCameras()
    
# Optimize Navvis Cameras
reprojectionError = 0.5
reconstructionUncertainty = 50
imageCount = 2
projectionAccuracy = 15
f = Metashape.TiePoints.Filter()
f.init(chunk, criterion = Metashape.TiePoints.Filter.ReprojectionError)
f.removePoints(reprojectionError)
chunk.optimizeCameras()
f.init(chunk, criterion = Metashape.TiePoints.Filter.ReconstructionUncertainty)
f.removePoints(reconstructionUncertainty)
chunk.optimizeCameras()
f.init(chunk, criterion = Metashape.TiePoints.Filter.ImageCount)
f.removePoints(imageCount)
chunk.optimizeCameras()
f.init(chunk, criterion = Metashape.TiePoints.Filter.ProjectionAccuracy)
f.removePoints(projectionAccuracy)
chunk.optimizeCameras()

doc.save()