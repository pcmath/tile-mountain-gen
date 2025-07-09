import numpy as np
from PIL import Image

def _isometric_projection(elevation, intensity, imgShape, fillValue = np.nan):
	W, H = elevation.shape[0], elevation.shape[1]
	img = np.full(imgShape, fillValue, dtype = intensity.dtype)
	for y in range(H-1,-1,-1):
		for x in range(W):
			elev = int(32 * elevation[x, y])
			new_y = min(y + elev, H)
			if new_y < 0:
				continue
			img[x, :new_y+1] = intensity[x, y]  # overwrite older values (painter's algo)
	return img

def isometric_projection(elevation, intensity):
	W, H = elevation.shape[0], elevation.shape[1]
	elev_max = int(32 * np.max(elevation))
	img_H = H #+ elev_max
	img_W = W
	if intensity.ndim == 2:
		return _isometric_projection(elevation, intensity, (img_W,img_H)).T
	nColor = intensity.shape[-1]
	img = np.empty((img_H, img_W, nColor), dtype = intensity.dtype)
	img2 = _isometric_projection(elevation, intensity, (img_W,img_H,nColor))
	for i in range(nColor):
		img[:,:,i] = img2[:,:,i].T
	return img