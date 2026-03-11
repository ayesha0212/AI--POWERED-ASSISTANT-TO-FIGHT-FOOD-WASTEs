import tensorflow as tf
import numpy as np
from PIL import Image

model = tf.keras.models.load_model("models/food_model.h5")

labels = ["rice","bread","vegetables","fruit","pasta"]

def classify_food(image):

    img = Image.open(image)
    img = img.resize((224,224))

    img = np.array(img)/255
    img = img.reshape(1,224,224,3)

    pred = model.predict(img)

    return labels[np.argmax(pred)]