import numpy as np

def unitVector(vector):
	unitVector = np.array(vector, dtype = float)
	return unitVector / np.linalg.norm(unitVector)

def computeLighting(elevation, lightDir=(1, 1, 1)):
	lightDir = np.array(lightDir, dtype=float)
	lightDir /= np.linalg.norm(lightDir)
	dz_dy, dz_dx = np.gradient(elevation)
	normal_x = -dz_dx
	normal_y = -dz_dy
	normal_z = np.ones_like(elevation)  # up direction
	norm = np.sqrt(normal_x**2 + normal_y**2 + normal_z**2)
	dot = (normal_x * lightDir[0] + normal_y * lightDir[1] + normal_z * lightDir[2]) / norm
	return np.clip(dot, 0, 1)

def computeSpecularMap(elevation, lightDir=(1, 1, 1), viewDir=(0, 0, 1), shininess=50):
	lightDir = unitVector(lightDir)
	viewDir = unitVector(viewDir)
	dz_dy, dz_dx = np.gradient(elevation)
	nx = -dz_dx
	ny = -dz_dy
	nz = np.ones_like(elevation)
	norm = np.sqrt(nx**2 + ny**2 + nz**2)
	nx /= norm
	ny /= norm
	nz /= norm
	hx = lightDir[0] + viewDir[0]
	hy = lightDir[1] + viewDir[1]
	hz = lightDir[2] + viewDir[2]
	h_norm = np.sqrt(hx**2 + hy**2 + hz**2)
	hx /= h_norm
	hy /= h_norm
	hz /= h_norm
	dot_nh = np.clip(nx * hx + ny * hy + nz * hz, 0, 1)
	specular = dot_nh ** shininess
	return specular

def applyLighting(mapRGB, mapLighting):
	shaded = mapRGB.astype(float) * mapLighting[..., np.newaxis]
	return np.clip(shaded, 0, 255).astype(np.uint8)