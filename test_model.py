from PIL import Image
import numpy as np

def classify_food(image):

    arr = np.array(image)
    avg = arr.mean()

    if avg < 80:
        return "bread"
    elif avg < 120:
        return "rice"
    elif avg < 160:
        return "vegetable"
    elif avg < 200:
        return "fruit"
    else:
        return "pasta"

img = Image.open("test.jpg")

result = classify_food(img)

print("Predicted Food:", result)