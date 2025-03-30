import os
import tkinter as tk
from tkinter import messagebox
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical
import cv2

MODEL_FILE = "mnist_model.keras"
if os.path.exists(MODEL_FILE):
    print("Loading model")
    model = load_model(MODEL_FILE)
else:
    print("Model not found, Train New Model (y/n): ")
    train=input()
    if train == "y" or train == "Y":   
        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        x_train, x_test = x_train / 255.0, x_test / 255.0
        y_train, y_test = to_categorical(y_train), to_categorical(y_test)

        model = Sequential([
            Flatten(input_shape=(28, 28)),
            Dense(128, activation='relu'),
            Dense(64, activation='relu'),
            Dense(10, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        model.fit(x_train, y_train, epochs=5, batch_size=32, validation_data=(x_test, y_test))
        model.save(MODEL_FILE)
        print(f"Model trained and saved as {MODEL_FILE}.")
    else:
        print("exiting.")

class NN:
    def __init__(self, model):
        self.model = model
        self.window = tk.Tk()
        self.window.title("Draw a Digit (28x28 Canvas)")
        
        self.canvas_width = 280
        self.canvas_height = 280
        self.grid_size = 28  
        self.cell_size = self.canvas_width // self.grid_size  

        self.canvas = tk.Canvas(self.window, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.grid(row=0, column=0, pady=20, padx=20)
        self.canvas.bind("<B1-Motion>", self.draw)
        
        self.predict_button = tk.Button(self.window, text="Predict", command=self.predict)
        self.predict_button.grid(row=1, column=0, pady=10)
        self.clear_button = tk.Button(self.window, text="Clear", command=self.clear_canvas)
        self.clear_button.grid(row=2, column=0, pady=10)

        self.image = np.zeros((self.canvas_height, self.canvas_width), dtype="uint8")

    def draw(self, event):
        x, y = event.x, event.y
        r = 8
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="black")
        cv2.circle(self.image, (x, y), r, (255), -1)

    def predict(self):
        resized = cv2.resize(self.image, (28, 28), interpolation=cv2.INTER_AREA)
        normalized = resized / 255.0  # Normalize image
        input_data = normalized.reshape(1, 28, 28)  # Reshape for the model
        prediction = np.argmax(self.model.predict(input_data))
        messagebox.showinfo("Yoda's prediction", f"After much thought and effort, Yoda predicts that the number is: {prediction}")

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image.fill(0)

    def run(self):
        self.window.mainloop()

app = NN(model)
app.run()
