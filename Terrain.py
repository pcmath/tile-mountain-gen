import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.ndimage import label
from PIL import Image
#===========================================
import MaskOperation

COLOR_DEFAULT_WATER = np.array([28, 107, 250])
COLOR_DEFAULT_ROCKS = np.array([160, 160, 160])
COLOR_DEFAULT_GRASS = np.array([48, 200, 48])

COLOR_DEFAULT_DICTIONARY = {
	"grass": COLOR_DEFAULT_GRASS,
	"water": COLOR_DEFAULT_WATER,
	"rocks": COLOR_DEFAULT_ROCKS
}

def sigmoid(x):
	return (1 + (np.exp(x)-np.exp(-x)) / (np.exp(x)+np.exp(-x)))/2

def makeRockTexture(shape, elevation, gradient, threshold, *, rockTextureIntensity = 10, **kwargs):
	rockTexture = np.random.rand(*shape) * 0.15
	rockTexture -= np.average(rockTexture)
	rockTexture = gaussian_filter(rockTexture, sigma = 0.75)
	rockTexture *= rockTextureIntensity * (gradient-threshold) * (gradient>threshold) / np.max(gradient-threshold)
	rockTexture *= np.clip(sigmoid( 2 * elevation ) - 0.5, 0, 1)
	return rockTexture

def assignTerrain(elevation, *, water_threshold=-0.01, slope_threshold=0.25/32, grassTexture = None,
		colors = None,
		**kwargs
	):
	if colors is None:
		colors = COLOR_DEFAULT_DICTIONARY
	h, w = elevation.shape
	tile_h = h // 32
	tile_w = w // 32
	if grassTexture is None:
		grassTexture = np.empty([32,32,3])
		grassTexture[:,:] = colors["grass"]
	mapRGB = np.tile(grassTexture, (tile_h, tile_w,1))
	gy, gx = np.gradient(elevation)
	gradient_magnitude = np.sqrt(gx**2 + gy**2)

	maskWater = elevation <= water_threshold
	maskRocks = (elevation > 0.1) & (gradient_magnitude > slope_threshold) & (elevation != 0)
	maskRocks = ~MaskOperation.removeSmallPools(~maskRocks, 28 ** 2) * ~maskWater & (elevation != 0)
	maskGrass = ~(maskWater | maskRocks)

	elevation[maskRocks] += makeRockTexture(elevation.shape, elevation, gradient_magnitude, slope_threshold, **kwargs)[maskRocks]
	mapRGB[maskRocks] = colors["rocks"]
	mapRGB[maskWater] = colors["water"]
	return mapRGB, maskGrass