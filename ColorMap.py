import numpy as np
from PIL import Image
from sklearn.neighbors import NearestNeighbors

def makeColorPalette(paletteImages):
	images = [img for img in paletteImages if img is not None]
	if not images:
		raise ValueError("Palette must contain at least one non-None image.")
	colors = np.unique(np.concatenate([img.reshape(-1, 3) for img in images], axis=0), axis = 0)
	return colors

def mapColor(sourceImage, paletteImages):
	colors = makeColorPalette(paletteImages)
	sourcePixels = sourceImage.reshape(-1, 3)
	_, indices = NearestNeighbors(n_neighbors=1).fit(colors).kneighbors(sourcePixels)
	mappedPixels = colors[indices.flatten()]
	return mappedPixels.reshape(sourceImage.shape[0], sourceImage.shape[1], 3).astype('uint8')
