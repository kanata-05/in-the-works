import os
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetV2L
from tensorflow.keras.applications.efficientnet_v2 import preprocess_input, decode_predictions
import cv2
from PIL import Image, ImageTk

MODEL = EfficientNetV2L(weights='imagenet')

class ImageRecognizer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Image Recognition")
        
        self.label = tk.Label(self.window, text="Upload an image to check", font=("Arial", 14))
        self.label.pack(pady=10)
        
        self.canvas = tk.Canvas(self.window, width=400, height=400, bg="white")
        self.canvas.pack()
        
        self.load_button = tk.Button(self.window, text="Upload Image", command=self.load_image)
        self.load_button.pack(pady=5)
        
        self.predict_button = tk.Button(self.window, text="Predict", command=self.predict)
        self.predict_button.pack(pady=5)
        
        self.image_path = None
        self.img_display = None
    
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.image_path = file_path
            img = Image.open(file_path)
            img.thumbnail((400, 400))
            self.img_display = ImageTk.PhotoImage(img)
            self.canvas.create_image(200, 200, image=self.img_display)
    
    def predict(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "Please upload an image first.")
            return
        
        img = tf.keras.preprocessing.image.load_img(self.image_path, target_size=(480, 480))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        predictions = MODEL.predict(img_array)
        decoded_preds = decode_predictions(predictions, top=5)[0]
        result_text = "\n".join([f"{label}: {prob:.2%}" for (_, label, prob) in decoded_preds])
        
        messagebox.showinfo("Prediction", result_text)
    
    def run(self):
        self.window.mainloop()

app = ImageRecognizer()
app.run()
