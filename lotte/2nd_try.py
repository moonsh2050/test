import os
import os, glob, numpy as np
from PIL import Image
import numpy as np
from numpy import asarray
from tensorflow.keras.models import Model, Sequential,load_model
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, Dropout, BatchNormalization, GlobalAveragePooling2D
from tensorflow.keras.layers import Activation
import tensorflow as tf
import scipy.signal as signal
from keras.applications.resnet50 import ResNet50,preprocess_input,decode_predictions
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from keras.callbacks import ReduceLROnPlateau
#########데이터 로드

# caltech_dir =  'C:/workspace/lotte/train/'
# categories = []
# for i in range(0,1000) :
#     i = "%d"%i
#     categories.append(i)

# nb_classes = len(categories)

# image_w = 128
# image_h = 128

# pixels = image_h * image_w * 3

# X = []
# y = []

# for idx, cat in enumerate(categories):
    
#     #one-hot 돌리기.
#     label = [0 for i in range(nb_classes)]
#     label[idx] = 1

#     image_dir = caltech_dir + "/" + cat
#     files = glob.glob(image_dir+"/*.jpg")
#     print(cat, " 파일 길이 : ", len(files))
#     for i, f in enumerate(files):
#         img = Image.open(f)
#         img = img.convert("RGB")
#         img = img.resize((image_w, image_h))
#         data = np.asarray(img)

#         X.append(data)
#         y.append(label)

#         if i % 700 == 0:
#             print(cat, " : ", f)

# X = np.array(X)
# y = np.array(y)

# np.save("C:/workspace/lotte/npy/x_0318.npy", arr=X)
# np.save("C:/workspace/lotte/npy/y_0318.npy", arr=y)
# x_pred = np.load("../data/npy/P_project_test.npy",allow_pickle=True)
x = np.load("C:/workspace/lotte/npy/x_0318.npy",allow_pickle=True)
y = np.load("C:/workspace/lotte/npy/y_0318.npy",allow_pickle=True)

print(x.shape)
print(y.shape)


# img1=[]
# for i in range(0,72000):
#     filepath='C:/workspace/lotte/test/test/%d.jpg'%i
#     image2=Image.open(filepath)
#     image2 = image2.convert('RGB')
#     image2 = image2.resize((128,128))
#     image_data2=asarray(image2)
#     # image_data2 = signal.medfilt2d(np.array(image_data2), kernel_size=3)
#     img1.append(image_data2)    

# # np.save('../data/csv/Dacon3/train4.npy', arr=img)
# np.save('C:/workspace/lotte/npy/test.npy', arr=img1)
# # alphabets = string.ascii_lowercase
# # alphabets = list(alphabets)


# x = np.load('../data/csv/Dacon3/train4.npy')
x_pred = np.load('C:/workspace/lotte/npy/test.npy',allow_pickle=True)


from tensorflow.keras.applications import EfficientNetB4, MobileNet
from tensorflow.keras.applications.efficientnet import preprocess_input


x = preprocess_input(x)
x_pred = preprocess_input(x_pred)

from sklearn.model_selection import train_test_split
x_train, x_val, y_train, y_val = train_test_split(x, y, train_size= 0.8, shuffle=True, random_state=66)

# eff = EfficientNetB4(weights='imagenet', include_top=False, input_shape=(128,128,3))
# eff.trainable = True
# top_model = eff.output
# top_model = GlobalAveragePooling2D()(top_model)
# top_model = Flatten()(top_model)
# top_model = (Dense(2048, activation='swish'))(top_model)
# top_model = (Dense(1000, activation='softmax'))(top_model)

# model = Model(inputs = eff.input, outputs = top_model)
# model.summary()

# from tensorflow.keras.optimizers import Adam
# optimizer = Adam(lr=0.001)
# model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
# from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
# es = EarlyStopping(monitor='val_loss', patience=21, mode='min')
# file_path = 'C:/workspace/lotte/h5/lotte_eff0319.hdf5'
# mc = ModelCheckpoint(file_path, monitor='val_accuracy',save_best_only=True,mode='max',verbose=1)
# rl = ReduceLROnPlateau(monitor='val_loss',factor=0.3,patience=8,verbose=1,mode='min')
# model.fit(x_train, y_train, batch_size=12, epochs=66, validation_data=(x_val, y_val),callbacks=[es,mc,rl])
# from tensorflow.keras.models import load_model
# from sklearn.metrics import r2_score

model = load_model('C:/workspace/lotte/h5/lotte_eff0319.hdf5')
loss, acc = model.evaluate(x_val, y_val)

result = model.predict(x_pred)

import pandas as pd
submission = pd.read_csv('C:/workspace/lotte/sample.csv')
submission['prediction'] = result.argmax(1)

submission.to_csv('C:/workspace/lotte/submit/lotte_eff0319.csv', index=False)