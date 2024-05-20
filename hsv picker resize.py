import cv2
import numpy as np
from tkinter import Tk, Label, Button, Scale, HORIZONTAL, filedialog, Frame, StringVar, Toplevel
from PIL import Image, ImageTk


class ColorSegmenter:
    def __init__(self, master):
        self.master = master
        self.master.title("Color Segmenter")

        self.load_button = Button(master, text="Load Image", command=self.load_image)
        self.load_button.pack()

        self.resize_button = Button(master, text="Resize Images", command=self.resize_images)
        self.resize_button.pack()

        self.reset_button = Button(master, text="Reset", command=self.reset)
        self.reset_button.pack()

        self.frame = Frame(master)
        self.frame.pack(fill="both", expand=True)

        self.original_image_label = Label(self.frame)
        self.original_image_label.grid(row=0, column=0, sticky="nsew")

        self.masked_image_label = Label(self.frame)
        self.masked_image_label.grid(row=0, column=1, sticky="nsew")

        self.hue_range = StringVar()
        self.sat_range = StringVar()
        self.val_range = StringVar()

        self.hue_frame = Frame(master)
        self.hue_frame.pack()
        self.hue_min = Scale(self.hue_frame, from_=0, to=179, orient=HORIZONTAL, label='Hue Min',
                             command=self.update_mask)
        self.hue_min.pack(side='left')
        self.hue_max = Scale(self.hue_frame, from_=0, to=179, orient=HORIZONTAL, label='Hue Max',
                             command=self.update_mask)
        self.hue_max.pack(side='left')
        self.hue_range_label = Label(self.hue_frame, textvariable=self.hue_range)
        self.hue_range_label.pack(side='left')

        self.sat_frame = Frame(master)
        self.sat_frame.pack()
        self.sat_min = Scale(self.sat_frame, from_=0, to=255, orient=HORIZONTAL, label='Saturation Min',
                             command=self.update_mask)
        self.sat_min.pack(side='left')
        self.sat_max = Scale(self.sat_frame, from_=0, to=255, orient=HORIZONTAL, label='Saturation Max',
                             command=self.update_mask)
        self.sat_max.pack(side='left')
        self.sat_range_label = Label(self.sat_frame, textvariable=self.sat_range)
        self.sat_range_label.pack(side='left')

        self.val_frame = Frame(master)
        self.val_frame.pack()
        self.val_min = Scale(self.val_frame, from_=0, to=255, orient=HORIZONTAL, label='Value Min',
                             command=self.update_mask)
        self.val_min.pack(side='left')
        self.val_max = Scale(self.val_frame, from_=0, to=255, orient=HORIZONTAL, label='Value Max',
                             command=self.update_mask)
        self.val_max.pack(side='left')
        self.val_range_label = Label(self.val_frame, textvariable=self.val_range)
        self.val_range_label.pack(side='left')

        self.selections = []

        # Set grid weights for resizing
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        self.image = None
        self.masked_image = None

        # Create zoom window
        self.zoom_window = Toplevel(self.master)
        self.zoom_window.title("Zoom Preview")
        self.zoom_image_label = Label(self.zoom_window)
        self.zoom_image_label.pack()

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = cv2.imread(file_path)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.original_image = self.image.copy()  # Store the original image
            self.display_image(self.image, self.original_image_label)
            self.update_mask()
            self.original_image_label.bind("<Button-1>", self.get_click_coordinates)
            self.original_image_label.bind("<Motion>", self.show_zoom_preview)

    def display_image(self, image, label):
        image = Image.fromarray(image)
        image_tk = ImageTk.PhotoImage(image)
        label.configure(image=image_tk)
        label.image = image_tk

    def get_click_coordinates(self, event):
        x, y = event.x, event.y
        if hasattr(self, 'image'):
            # Adjust coordinates to the image size
            width, height = self.image.shape[1], self.image.shape[0]
            resized_width, resized_height = self.original_image_label.winfo_width(), self.original_image_label.winfo_height()
            x = int(x * (width / resized_width))
            y = int(y * (height / resized_height))

            hsv_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2HSV)
            hsv_value = hsv_image[y, x]
            self.selections.append(hsv_value)
            self.calculate_hsv_range()
            self.resize_images()  # Resize images after each click

    def calculate_hsv_range(self):
        if self.selections:
            selections_array = np.array(self.selections)
            self.hue_min.set(np.min(selections_array[:, 0]))
            self.hue_max.set(np.max(selections_array[:, 0]))
            self.sat_min.set(np.min(selections_array[:, 1]))
            self.sat_max.set(np.max(selections_array[:, 1]))
            self.val_min.set(np.min(selections_array[:, 2]))
            self.val_max.set(np.max(selections_array[:, 2]))
            self.update_mask()

    def update_mask(self, val=None):
        if hasattr(self, 'image'):
            hsv_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2HSV)
            lower_hsv = np.array([self.hue_min.get(), self.sat_min.get(), self.val_min.get()])
            upper_hsv = np.array([self.hue_max.get(), self.sat_max.get(), self.val_max.get()])

            self.hue_range.set(f'Hue: {self.hue_min.get()} - {self.hue_max.get()}')
            self.sat_range.set(f'Saturation: {self.sat_min.get()} - {self.sat_max.get()}')
            self.val_range.set(f'Value: {self.val_min.get()} - {self.val_max.get()}')

            mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)
            self.masked_image = cv2.bitwise_and(self.image, self.image, mask=mask)
            self.display_image(self.masked_image, self.masked_image_label)

    def reset(self):
        self.selections = []
        self.hue_min.set(0)
        self.hue_max.set(179)
        self.sat_min.set(0)
        self.sat_max.set(255)
        self.val_min.set(0)
        self.val_max.set(255)
        self.hue_range.set('')
        self.sat_range.set('')
        self.val_range.set('')
        if hasattr(self, 'image'):
            self.display_image(self.image, self.masked_image_label)

    def resize_images(self):
        self.update_display_images()

    def update_display_images(self):
        if self.image is not None:
            # Resize original image
            orig_width, orig_height = self.original_image.shape[1], self.original_image.shape[0]
            resized_width, resized_height = self.original_image_label.winfo_width(), self.original_image_label.winfo_height()
            aspect_ratio = orig_width / orig_height

            if resized_width / resized_height > aspect_ratio:
                new_height = resized_height
                new_width = int(new_height * aspect_ratio)
            else:
                new_width = resized_width
                new_height = int(new_width / aspect_ratio)

            resized_image = cv2.resize(self.original_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            self.display_image(resized_image, self.original_image_label)

            # Resize masked image
            if self.masked_image is not None:
                resized_masked_image = cv2.resize(self.masked_image, (new_width, new_height),
                                                  interpolation=cv2.INTER_AREA)
                self.display_image(resized_masked_image, self.masked_image_label)

    def show_zoom_preview(self, event):
        if self.image is not None:
            zoom_size = 50  # Size of the zoomed-in region
            zoom_factor = 4  # How much to zoom in
            x, y = event.x, event.y

            # Adjust coordinates to the image size
            width, height = self.image.shape[1], self.image.shape[0]
            resized_width, resized_height = self.original_image_label.winfo_width(), self.original_image_label.winfo_height()
            x = int(x * (width / resized_width))
            y = int(y * (height / resized_height))

            # Define the zoomed-in region
            x1 = max(0, x - zoom_size)
            y1 = max(0, y - zoom_size)
            x2 = min(width, x + zoom_size)
            y2 = min(height, y + zoom_size)
            zoomed_image = self.image[y1:y2, x1:x2]

            # Resize the zoomed-in region
            zoomed_image = cv2.resize(zoomed_image, (zoom_size * zoom_factor, zoom_size * zoom_factor),
                                      interpolation=cv2.INTER_LINEAR)

            # Draw a crosshair in the center
            center_x, center_y = zoom_size * zoom_factor // 2, zoom_size * zoom_factor // 2
            cv2.drawMarker(zoomed_image, (center_x, center_y), (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=20,
                           thickness=2)

            self.display_image(zoomed_image, self.zoom_image_label)


def main():
    root = Tk()
    app = ColorSegmenter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
