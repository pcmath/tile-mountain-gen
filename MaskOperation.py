import numpy as np
from scipy.ndimage import label
from scipy.spatial import distance

def inner(array):
	padded = np.pad(array, pad_width=1, mode='constant', constant_values=False)
	up    = padded[:-2, 1:-1]
	down  = padded[2:, 1:-1]
	left  = padded[1:-1, :-2]
	right = padded[1:-1, 2:]
	neighbor_false = (~up) | (~down) | (~left) | (~right)
	output = array & ~neighbor_false
	return output

def removeSmallPools(array, minSize = 30 * 30):
		labeled, nFeatures = label(array)
		componentSizes = np.bincount(labeled.ravel())
		keepMask = componentSizes >= minSize
		keepMask[0] = 0  # always remove background
		cleanedArray = keepMask[labeled]
		return cleanedArray

def getBounds(mask):
	nDim = mask.ndim
	indices = np.where(mask)
	bounds = np.zeros((nDim, 2), dtype = int)
	for i in range(nDim):
		bounds[i,0] = np.min(indices[i])
		bounds[i,1] = np.max(indices[i])
	return bounds

def getNonzeroSlice(array, margin=2):
	mask = array != 0
	nDim = array.ndim
	if not np.any(mask):
		return (slice(0, 1),) * nDim
	dax = getBounds(mask)
	slices = ()
	for n in range(nDim):
		dax[n][0] = max(dax[n][0] - margin, 0)
		dax[n][1] = min(dax[n][1] + margin, array.shape[n])
		slices += (slice(*dax[n]),)
	return slices