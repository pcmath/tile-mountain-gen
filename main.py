import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import numpy as np
from PIL import Image, ImageTk
import json
#=============================
from gui.JsonInterface import JsonInterface
import MainGenerator

APP_TITLE = "Tiled Mountain Generator"
ENTRY_BOX_WIDTH = 3
MAX_ENTRY_VAL = 5
SIZE_TILE = 32
TEXT_BUTTON_GENERATE = "Generate"
TEXT_BUTTON_EXPORT = "Export Image"
TEXT_BUTTON_GRASS = "Select Grass Texture"

with open("mountain-generator-params.json", 'r') as openfile:
	parameters = json.load(openfile)


class TileMapMenu(JsonInterface):
	def __init__(self, nX, nY, parameters):
		self.nX = nX
		self.nY = nY
		self.root = tk.Tk()
		self.root.title(APP_TITLE)
		self.inputFrame = tk.Frame(self.root)
		self.imageFrame = tk.Frame(self.root)
		self.configInputFrame(self.inputFrame)
		self.configImageFrame(self.imageFrame)
		self.inputFrame.pack(side=tk.LEFT)
		self.imageFrame.pack(side=tk.RIGHT)
		self.textureGrass = None
		self.parameters = parameters
		super().__init__(self.root)
		self.root.mainloop()

	def buttonActionGenerate(self):
		elevation = np.fliplr(self.getEntryArray())
		self.imageArray = np.flipud(MainGenerator.makeImage(
			elevation,
			grass = self.textureGrass,
			**self.parameters,
		))
		self.img = ImageTk.PhotoImage(image=Image.fromarray(self.imageArray))
		self.canvas.itemconfig(self.imageContainer, image=self.img)

	def buttonActionGrass(self):
		filePath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
		if not filePath:
			return
		self.textureGrass = np.array(Image.open(filePath).convert("RGB"))

	def configImageFrame(self, master):
		grassTextureButton = ttk.Button(
			master,
			text = TEXT_BUTTON_GRASS,
			command = self.buttonActionGrass
		)
		grassTextureButton.pack()
		generateButton = ttk.Button(
			master,
			text = TEXT_BUTTON_GENERATE,
			command = self.buttonActionGenerate
		)
		generateButton.pack()
		self.configImageCanvas(master)
		exportButton = tk.Button(master, text = TEXT_BUTTON_EXPORT, command = self.exportImage)
		exportButton.pack()

	def exportImage(self):
		if self.imageArray is None:
			return
		filePath = filedialog.asksaveasfilename(defaultextension = ".png", filetypes=[("PNG files", "*.png")])
		if not filePath:
			return
		img = Image.fromarray(self.imageArray)
		img.save(filePath)

	def configImageCanvas(self, master, sizeTile = SIZE_TILE):
		w, h = self.nX * sizeTile, self.nY * sizeTile
		self.imageArray = np.zeros( (w, h, 3), dtype = np.uint8)
		self.img = ImageTk.PhotoImage(image = Image.fromarray(self.imageArray))
		canvas = tk.Canvas(master, width = w, height = h)
		canvas.pack()
		self.imageContainer = canvas.create_image(w, 10, anchor = "ne", image = self.img)
		self.canvas = canvas

	def configInputFrame(self, master):
		self.entryArray = self.configEntryArray(master)

	def configEntryArray(self, master):
		for xi in range(self.nX):
			master.columnconfigure(xi)
		for yi in range(self.nY):
			master.rowconfigure(yi)
		entryArray = []
		for xi in range(self.nX):
			entryArray += [self.makeEntryColumn(xi, master)]
		return entryArray

	def makeEntryColumn(self, xi, master):
		entryColumn = []
		for yi in range(self.nY):
			entryColumn += [self.makeEntry(xi, yi, master)]
		return entryColumn

	def makeEntry(self, x, y, master, width = ENTRY_BOX_WIDTH):
		entry = tk.Entry(master, width = width)
		entry.insert(0, '0')
		entry.bind("<Up>", lambda e, row=y, col=x: self.moveFocus(col, row - 1))
		entry.bind("<Down>", lambda e, row=y, col=x: self.moveFocus(col, row + 1))
		entry.bind("<Left>", lambda e, row=y, col=x: self.moveFocus(col - 1, row))
		entry.bind("<Right>", lambda e, row=y, col=x: self.moveFocus(col + 1, row))
		entry.bind("<KeyRelease>", lambda e, ent=entry: self.updateEntryColor(ent))
		entry.grid(column = x, row = y, padx = 0, pady = 0)
		return entry

	def moveFocus(self, xi, yi):
		xi = np.clip(xi, 0, self.nX - 1)
		yi = np.clip(yi, 0, self.nY - 1)
		self.entryArray[xi][yi].focus_set()
		self.entryArray[xi][yi].select_range(0, 'end')

	def getEntryArray(self):
		entryArray = np.empty((self.nX,self.nY), dtype = float)
		for xi in range(self.nX):
			for yi in range(self.nY):
				entryArray[xi,yi] = self.getEntryValue(self.entryArray[xi][yi])
		return entryArray

	def getEntryValue(self, entry, defaultValue = 0):
		try:
			return float(entry.get())
		except ValueError:
			return defaultValue

	def getFileData(self):
		return self.getEntryArray().tolist()

	def loadFileData(self, data):
		for xi in range(self.nX):
			for yi in range(self.nY):
				val = data[xi][yi]
				entry = self.entryArray[xi][yi]
				entry.delete(0, tk.END)
				entry.insert(0, str(val))
				self.updateEntryColor(entry)

	def updateEntryColor(self, entry):
		val = self.getEntryValue(entry)
		norm = max(0.0, min(1.0, val / MAX_ENTRY_VAL))
		shade = int(255 * (1.0 - norm))
		color = f"#{shade:02x}{shade:02x}{shade:02x}"
		entry.config(bg = color)

TileMapMenu(parameters["dimensions"]["x"], parameters["dimensions"]["y"], parameters)