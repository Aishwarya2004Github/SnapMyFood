import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2, InceptionV3
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# Laptop ko heating se bachane ke liye config
IMG_SIZE = (224, 224)
BATCH_SIZE = 16 # Isko kam rakha hai taaki RAM aur CPU par load kam pade

datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    horizontal_flip=True
)

train_gen = datagen.flow_from_directory('dataset_images', target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode='categorical', subset='training')
val_gen = datagen.flow_from_directory('dataset_images', target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode='categorical', subset='validation')

# Model 1: MobileNetV2 (Very Fast)
base1 = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base1.trainable = False
x1 = GlobalAveragePooling2D()(base1.output)
x1 = Dense(256, activation='relu')(x1)
out1 = Dense(len(train_gen.class_indices), activation='softmax')(x1)
model1 = Model(inputs=base1.input, outputs=out1)

# Model 2: InceptionV3 (Ghevar jaise complex patterns ke liye best)
base2 = InceptionV3(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base2.trainable = False
x2 = GlobalAveragePooling2D()(base2.output)
out2 = Dense(len(train_gen.class_indices), activation='softmax')(x2)
model2 = Model(inputs=base2.input, outputs=out2)

model1.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model2.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Callbacks: Ye laptop ko overheat hone se bachayenge
callbacks = [
    EarlyStopping(monitor='val_loss', patience=12, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5)
]

print("Step 1: Training MobileNet...")
model1.fit(train_gen, validation_data=val_gen, epochs=30, callbacks=callbacks)

print("Step 2: Training Inception...")
model2.fit(train_gen, validation_data=val_gen, epochs=30, callbacks=callbacks)

model1.save('model_mobilenet.h5')
model2.save('model_inception.h5') # Resnet ki jagah Inception better hai

with open('classes.txt', 'w') as f:
    for cls in train_gen.class_indices.keys():
        f.write(cls + '\n')