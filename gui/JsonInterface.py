import tkinter as tk
from tkinter import filedialog
import json

class JsonInterface:
	def __init__(self, master):
		menubar = tk.Menu(master)
		fileMenu = tk.Menu(menubar, tearoff=0)
		fileMenu.add_command(label = "Save", command = self.fileSave)
		fileMenu.add_command(label = "Open", command = self.fileOpen)
		menubar.add_cascade(label = "File", menu = fileMenu)
		master.config(menu = menubar)

	def fileSave(self):
		data = self.getFileData()
		filePath = filedialog.asksaveasfilename(
			defaultextension=".json",
			filetypes=[("JSON files", "*.json")],
			title="Save Grid Values"
		)
		if not filePath:
			return
		with open(filePath, 'w') as f:
			json.dump(data, f)
		
	def fileOpen(self):
		filePath = filedialog.askopenfilename(
			filetypes=[("JSON files", "*.json")],
			title="Load File"
		)
		if not filePath:
			return
		with open(filePath, 'r') as f:
			data = json.load(f)
			self.loadFileData(data)