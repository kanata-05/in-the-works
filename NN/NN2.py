import os
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import cv2
import torch
from PIL import Image, ImageTk
from ultralytics import YOLO
from transformers import CLIPProcessor, CLIPModel

yolo_model = YOLO("yolov8x.pt")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

class ImageRecognizer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Image Recognition")
        self.label = tk.Label(self.window, text="Upload an image", font=("Arial", 14))
        self.label.pack(pady=10)
        self.canvas = tk.Canvas(self.window, width=500, height=500, bg="white")
        self.canvas.pack()
        self.load_button = tk.Button(self.window, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=5)
        self.predict_button = tk.Button(self.window, text="Detect Objects", command=self.detect_objects)
        self.predict_button.pack(pady=5)
        self.image_path = None
        self.img_display = None
    
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.image_path = file_path
            img = Image.open(file_path)
            img.thumbnail((500, 500))
            self.img_display = ImageTk.PhotoImage(img)
            self.canvas.create_image(250, 250, image=self.img_display)
    
    def detect_objects(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "Please upload an image first.")
            return
        results = yolo_model(self.image_path)
        detections = results[0].boxes.data.cpu().numpy()
        img = cv2.imread(self.image_path)
        for det in detections:
            x1, y1, x2, y2, conf, cls = det
            label = results[0].names[int(cls)]
            conf = f"{conf:.2f}"
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(img, f"{label} ({conf})", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imwrite("detected.jpg", img)
        image = Image.open(self.image_path)
        inputs = clip_processor(images=image, return_tensors="pt")
        outputs = clip_model.get_image_features(**inputs)
        messagebox.showinfo("Detection Complete", "Objects detected and highlighted.")
        img = Image.open("detected.jpg")
        img.thumbnail((500, 500))
        self.img_display = ImageTk.PhotoImage(img)
        self.canvas.create_image(250, 250, image=self.img_display)
    
    def run(self):
        self.window.mainloop()

app = ImageRecognizer()
app.run()
