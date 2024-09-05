import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import importlib.util

class PhotoSweatshopCarbon(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PhotoSweatshop Carbon')
        self.geometry('1000x800')
        self.layers = []
        self.current_layer = None
        self.create_widgets()
        self.bind_shortcuts()

    def create_widgets(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_image)
        file_menu.add_command(label="Save", command=self.save_image)
        file_menu.add_command(label="Exit", command=self.quit)

        sidebar = tk.Frame(self, width=200, bg='lightgray')
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.layer_listbox = tk.Listbox(sidebar)
        self.layer_listbox.pack(fill=tk.Y, padx=10, pady=10)
        self.layer_listbox.bind('<<ListboxSelect>>', self.select_layer)

        self.show_hide_button = tk.Button(sidebar, text="Show/Hide Layer", command=self.toggle_layer_visibility)
        self.show_hide_button.pack(padx=10, pady=5)

        control_frame = tk.Frame(sidebar)
        control_frame.pack(padx=10, pady=5)

        self.brightness_scale = tk.Scale(control_frame, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, label="Brightness", command=self.adjust_brightness)
        self.brightness_scale.set(1.0)
        self.brightness_scale.pack()

        self.contrast_scale = tk.Scale(control_frame, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, label="Contrast", command=self.adjust_contrast)
        self.contrast_scale.set(1.0)
        self.contrast_scale.pack()

        self.color_scale = tk.Scale(control_frame, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, label="Color", command=self.adjust_color)
        self.color_scale.set(1.0)
        self.color_scale.pack()

        self.plugin_button = tk.Button(control_frame, text="Load Plugin", command=self.load_plugin_dialog)
        self.plugin_button.pack(pady=10)

        self.rotate_button = tk.Button(control_frame, text="Rotate 90°", command=self.rotate_image)
        self.rotate_button.pack(pady=10)

        self.crop_button = tk.Button(control_frame, text="Crop", command=self.crop_image)
        self.crop_button.pack(pady=10)

        self.filter_button = tk.Button(control_frame, text="Apply Filter", command=self.apply_filter)
        self.filter_button.pack(pady=10)

        self.image_frame = tk.Frame(self, width=800, height=600, bg='white', relief=tk.SUNKEN, bd=2)
        self.image_frame.pack(pady=20, padx=20, expand=True)
        self.image_frame.pack_propagate(False)
        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(expand=True)

    def bind_shortcuts(self):
        self.bind('<Control-r>', self.reset_image)
        self.bind('<Control-p>', self.reset_sliders)

    def open_image(self):
        image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if image_path:
            image = Image.open(image_path)
            self.add_layer(image, image_path)

    def save_image(self):
        if self.layers:
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg")])
            if save_path:
                final_image = self.merge_layers()
                final_image.save(save_path)

    def add_layer(self, image, name):
        self.layers.append({'image': image, 'name': name, 'visible': True, 'original': image.copy()})
        self.layer_listbox.insert(tk.END, name)
        self.select_layer(len(self.layers) - 1)

    def select_layer(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.current_layer = self.layers[index]
            self.display_image()

    def toggle_layer_visibility(self):
        selection = self.layer_listbox.curselection()
        if selection:
            index = selection[0]
            self.layers[index]['visible'] = not self.layers[index]['visible']
            self.display_image()

    def display_image(self):
        if self.layers:
            base_image = self.layers[0]['image'].copy()
            for layer in self.layers[1:]:
                if layer['visible']:
                    base_image.paste(layer['image'], (0, 0), layer['image'])
            img = base_image.copy()
            img.thumbnail((800, 600))
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk

    def merge_layers(self):
        if not self.layers:
            return None
        base_image = self.layers[0]['image'].copy()
        for layer in self.layers[1:]:
            if layer['visible']:
                base_image.paste(layer['image'], (0, 0), layer['image'])
        return base_image

    def adjust_brightness(self, value):
        if self.current_layer:
            enhancer = ImageEnhance.Brightness(self.current_layer['original'])
            self.current_layer['image'] = enhancer.enhance(float(value))
            self.display_image()

    def adjust_contrast(self, value):
        if self.current_layer:
            enhancer = ImageEnhance.Contrast(self.current_layer['original'])
            self.current_layer['image'] = enhancer.enhance(float(value))
            self.display_image()

    def adjust_color(self, value):
        if self.current_layer:
            enhancer = ImageEnhance.Color(self.current_layer['original'])
            self.current_layer['image'] = enhancer.enhance(float(value))
            self.display_image()

    def rotate_image(self):
        if self.current_layer:
            self.current_layer['image'] = self.current_layer['original'].rotate(90, expand=True)
            self.current_layer['original'] = self.current_layer['image'].copy()
            self.display_image()

    def crop_image(self):
        if self.current_layer:
            width, height = self.current_layer['original'].size
            left, top, right, bottom = width // 4, height // 4, 3 * width // 4, 3 * height // 4
            self.current_layer['image'] = self.current_layer['original'].crop((left, top, right, bottom))
            self.current_layer['original'] = self.current_layer['image'].copy()
            self.display_image()

    def apply_filter(self):
        if self.current_layer:
            self.current_layer['image'] = self.current_layer['original'].filter(ImageFilter.BLUR)
            self.current_layer['original'] = self.current_layer['image'].copy()
            self.display_image()

    def reset_image(self, event=None):
        if self.current_layer:
            self.current_layer['image'] = self.current_layer['original'].copy()
            self.display_image()

    def reset_sliders(self, event=None):
        self.brightness_scale.set(1.0)
        self.contrast_scale.set(1.0)
        self.color_scale.set(1.0)

    def load_plugin_dialog(self):
        plugin_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if plugin_path:
            self.load_plugin(plugin_path)

    def load_plugin(self, plugin_path):
        spec = importlib.util.spec_from_file_location("plugin", plugin_path)
        plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin)
        plugin.apply(self.current_layer['image'].filename)

if __name__ == '__main__':
    app = PhotoSweatshopCarbon()
    app.mainloop()
