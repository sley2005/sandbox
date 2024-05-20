import cv2
import numpy as np
from tkinter import Tk, Label, Button, Scale, HORIZONTAL, filedialog, Frame, StringVar
from PIL import Image, ImageTk

class ColorSegmenter:
    def __init__(self, master):
        self.master = master
        self.master.title("Color Segmenter")

        self.load_button = Button(master, text="Load Image", command=self.load_image)
        self.load_button.pack()

        self.reset_button = Button(master, text="Reset", command=self.reset)
        self.reset_button.pack()

        self.frame = Frame(master)
        self.frame.pack()

        self.original_image_label = Label(self.frame)
        self.original_image_label.grid(row=0, column=0)
        
        self.masked_image_label = Label(self.frame)
        self.masked_image_label.grid(row=0, column=1)

        # HSV range display
        self.hue_range = StringVar()
        self.sat_range = StringVar()
        self.val_range = StringVar()

        self.hue_frame = Frame(master)
        self.hue_frame.pack()
        self.hue_min = Scale(self.hue_frame, from_=0, to=179, orient=HORIZONTAL, label='Hue Min', command=self.update_mask)
        self.hue_min.pack(side='left')
        self.hue_max = Scale(self.hue_frame, from_=0, to=179, orient=HORIZONTAL, label='Hue Max', command=self.update_mask)
        self.hue_max.pack(side='left')
        self.hue_range_label = Label(self.hue_frame, textvariable=self.hue_range)
        self.hue_range_label.pack(side='left')

        self.sat_frame = Frame(master)
        self.sat_frame.pack()
        self.sat_min = Scale(self.sat_frame, from_=0, to=255, orient=HORIZONTAL, label='Saturation Min', command=self.update_mask)
        self.sat_min.pack(side='left')
        self.sat_max = Scale(self.sat_frame, from_=0, to=255, orient=HORIZONTAL, label='Saturation Max', command=self.update_mask)
        self.sat_max.pack(side='left')
        self.sat_range_label = Label(self.sat_frame, textvariable=self.sat_range)
        self.sat_range_label.pack(side='left')

        self.val_frame = Frame(master)
        self.val_frame.pack()
        self.val_min = Scale(self.val_frame, from_=0, to=255, orient=HORIZONTAL, label='Value Min', command=self.update_mask)
        self.val_min.pack(side='left')
        self.val_max = Scale(self.val_frame, from_=0, to=255, orient=HORIZONTAL, label='Value Max', command=self.update_mask)
        self.val_max.pack(side='left')
        self.val_range_label = Label(self.val_frame, textvariable=self.val_range)
        self.val_range_label.pack(side='left')

        self.selections = []

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = cv2.imread(file_path)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.display_image(self.image, self.original_image_label)
            self.update_mask()
            self.original_image_label.bind("<Button-1>", self.get_click_coordinates)

    def display_image(self, image, label):
        image = Image.fromarray(image)
        image_tk = ImageTk.PhotoImage(image)
        label.configure(image=image_tk)
        label.image = image_tk

    def get_click_coordinates(self, event):
        x, y = event.x, event.y
        if hasattr(self, 'image'):
            hsv_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2HSV)
            hsv_value = hsv_image[y, x]
            self.selections.append(hsv_value)
            self.calculate_hsv_range()

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
            masked_image = cv2.bitwise_and(self.image, self.image, mask=mask)
            self.display_image(masked_image, self.masked_image_label)

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

def main():
    root = Tk()
    app = ColorSegmenter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
