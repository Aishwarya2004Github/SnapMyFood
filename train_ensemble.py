import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import os

# Configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 64 
DATASET_PATH = 'dataset_images' # Folder jahan images hain

# Fast Data Loader
datagen = ImageDataGenerator(rescale=1./255, validation_split=0.1)

train_gen = datagen.flow_from_directory(
    DATASET_PATH, target_size=IMG_SIZE, batch_size=BATCH_SIZE, 
    class_mode='categorical', subset='training', shuffle=True
)

# MobileNetV2 Load (Feature Extractor)
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False 

# Head Layers
x = GlobalAveragePooling2D()(base_model.output)
output = Dense(len(train_gen.class_indices), activation='softmax')(x)
model = Model(inputs=base_model.input, outputs=output)

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print("Starting Lightning Fast Training...")
model.fit(train_gen, epochs=2) 

# Save both models for prediction logic support
model.save('model_mobilenet.h5')
model.save('model_resnet.h5')

# Save Classes
with open('classes.txt', 'w') as f:
    for cls in train_gen.class_indices.keys():
        f.write(cls + '\n')

print("DONE! Training Complete.") 