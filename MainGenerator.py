import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.ndimage import zoom
from scipy.interpolate import RectBivariateSpline
from PIL import Image
#===========================================================
import Terrain
import Isometric
import Shader
import ColorMap
import Upscale
from MaskOperation import inner
#===========================================================
# Constants
LIGHT_DIR = (-0.4, -1, 1.4)
WATER_LEVEL = -0.1

def warpArray(array, strength=8, scale=8):
	shape = array.shape
	nDim = array.ndim
	noise = gaussian_filter(np.random.randn(nDim, *shape), sigma = (0,) + (scale,) * nDim)
	noise *= strength / np.max(np.abs(noise))
	ranges = [np.arange(length) for length in shape]
	baseCoords = np.meshgrid(*ranges, indexing='ij')
	warpCoords = [np.clip(baseCoords[n] + noise[n], 0, shape[n] - 1) for n in range(nDim)]
	warped = map_coordinates(array, warpCoords, order=1, mode='reflect')
	return warped

def fractionalBrownianMotion(shape, level, period = 70):
	yy, xx = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]), indexing='ij')
	result = np.zeros(shape)
	for i in range(1,25):
		I =  0.9 ** i
		v = (np.random.rand(2)-0.5)*2
		v_hat = v / np.linalg.norm(v)
		result += (np.exp(np.sin( (xx * v_hat[0]+yy * v_hat[1]) * np.pi / period * i))-np.exp(1)) * I
	result *= level / np.max(result)
	return result

def makeNormalizedSpecularMap(mapHeight, lightDirection, waterMask):
	if ~np.any(waterMask):
		return 0
	specular_map = Shader.computeSpecularMap(32 * mapHeight, light_dir = lightDirection, view_dir=(0, 1, 1))
	specular_map *= inner(waterMask)
	specular_map[inner(waterMask)] -= np.min(specular_map[inner(waterMask)])
	specular_map = np.clip(specular_map, 0, np.percentile(specular_map[specular_map!=0], 99))
	specular_map /= np.max(specular_map)
	return specular_map

def makeImage(elevation, *, palettePath, grass = None, lightDirection = LIGHT_DIR, tileSize = 32, **kwargs):
	mapHeight = Upscale.upscale_array(elevation)
	mapHeight2 = zoom(elevation.astype(float), zoom=32, order=1)
	mask = (mapHeight2 < 0) | (mapHeight == np.nan)
	mapHeight[mask] = mapHeight2[mask]
	mask_type = Upscale.repeatUpscale(elevation, tileSize)
	mask_type_grass = (-0.01 < mask_type) & (mask_type < 0.01)
	mapHeight *= ~mask_type_grass
	mapHeight[~mask_type_grass] = warpArray(warpArray(mapHeight), strength=4, scale=4)[~mask_type_grass]
	mapRGB, grass_mask = Terrain.assignTerrain(mapHeight, water_threshold=WATER_LEVEL, grassTexture = grass, **kwargs)
	water_mask = mapHeight <= WATER_LEVEL
	if np.any(water_mask):
		water_intensity = np.abs(mapHeight * water_mask) + WATER_LEVEL / 4
		waterElevation = fractionalBrownianMotion(mapHeight.shape, WATER_LEVEL/4) * water_intensity
		mapHeight[water_mask] = WATER_LEVEL + 8 * waterElevation[water_mask]
	lighting = Shader.computeLighting(32 * mapHeight.astype(float), lightDir = lightDirection)
	normLight = Shader.computeLighting(np.zeros( (3,3) ), lightDir = lightDirection)[1,1]
	normLight -= np.min(lighting)
	lighting -= np.min(lighting)
	lighting /= normLight
	lighting[mask_type_grass] = 1
	if np.any(water_mask):
		lighting[inner(water_mask)] -= np.min(lighting[inner(water_mask)])
		lighting[inner(water_mask)] /= np.max(lighting[inner(water_mask)])
	lighting += 3 * makeNormalizedSpecularMap(mapHeight, lightDirection, water_mask)
	mapRGB = Shader.applyLighting(mapRGB, lighting)
	refImage = np.array(Image.open(palettePath).convert("RGB"))
	if grass is None:
		mapRGB = ColorMap.mapColor(mapRGB, [refImage])
	else:
		mapRGB[grass_mask] = ColorMap.mapColor(mapRGB, [grass])[grass_mask]
		mapRGB[~grass_mask] = ColorMap.mapColor(mapRGB, [refImage])[~grass_mask]
	return Isometric.isometric_projection(mapHeight, mapRGB)