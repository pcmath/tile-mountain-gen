import numpy as np
from scipy.interpolate import griddata
import MaskOperation
#================================================
from MaskOperation import inner

def repeatUpscale(array, scale):
	upscaledArray = array
	for i in range(array.ndim):
		upscaledArray = np.repeat(upscaledArray, scale, axis = i)
	return upscaledArray

def upscale_array(elevation, scale=32):
	X, Y = elevation.shape
	xi, yi = np.where( elevation != 0 )
	nMountain = len(xi)
	upscaled = repeatUpscale(elevation, scale)
	nonGrass = upscaled != 0
	#upscaled[nonGrass & ~inner(nonGrass)] = 0 #set the bordering to 0 for smoother tile transition
	#For some reason, this messes up the mountains and causes them to part
	upscaled[upscaled != 0] = np.nan
	for i in range(nMountain):
		upscaled[32 * xi[i] + 16, 32 * yi[i] + 16] = elevation[xi[i],yi[i]]
	mySlice = MaskOperation.getNonzeroSlice(upscaled,3)
	nan_mask = np.isnan(upscaled)
	points_mask = np.zeros(nan_mask.shape, dtype = bool)
	points_mask[mySlice] = True
	points_mask *= ~nan_mask
	known_points = np.column_stack(np.where(points_mask))
	known_values = upscaled[points_mask]
	unknown_points = np.column_stack(np.where(nan_mask))
	interpolated = griddata(known_points, known_values, unknown_points, method='linear')
	upscaled[nan_mask] = interpolated
	return upscaled
