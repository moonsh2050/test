import numpy as np
import pandas as pd
import os
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.efficientnet import EfficientNetB4,EfficientNetB0,EfficientNetB7
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img
from tensorflow.keras.models import Sequential, load_model, Model
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, BatchNormalization, Flatten, Dropout, GlobalAveragePooling2D, Input, GaussianDropout
from tensorflow.keras.activations import swish
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from scipy import stats
from cutmix_keras import CutMixImageDataGenerator
filenum = 5
batch = 6
seed = 42
dropout = 0.4
epochs = 500
model_path = 'C:/workspace/lotte/h5/lpd_{0:03}.hdf5'.format(filenum)
save_folder = 'C:/workspace/lotte/submit/submit_{0:03}'.format(filenum)
sub = pd.read_csv('C:/workspace/lotte/sample.csv', header = 0)
es = EarlyStopping(patience = 7)
lr = ReduceLROnPlateau(factor = 0.3, patience = 3, verbose = 1)
cp = ModelCheckpoint(model_path, save_best_only= True)

if not os.path.exists(save_folder):
    os.mkdir(save_folder)

#1. 데이터
train_gen = ImageDataGenerator(
    validation_split = 0.2,
    width_shift_range= 0.05,
    height_shift_range= 0.05,
    preprocessing_function= preprocess_input, #밖에 쓸떄랑 안에서 쓸때 확인
    horizontal_flip= True
)

test_gen = ImageDataGenerator(
    preprocessing_function= preprocess_input,
    width_shift_range= 0.03,
    height_shift_range= 0.03
)

# Found 39000 images belonging to 1000 classes.
train_data = train_gen.flow_from_directory(
    'C:/workspace/lotte/train_new2',
    target_size = (120, 120),
    class_mode = 'sparse',
    batch_size = batch,
    seed = seed,
    subset = 'training'
)

# Found 9000 images belonging to 1000 classes.
val_data = train_gen.flow_from_directory(
    'C:/workspace/lotte/train_new2',
    target_size = (120, 120),
    class_mode = 'sparse',
    batch_size = batch,
    seed = seed,
    subset = 'validation'
)

# train_data = CutMixImageDataGenerator(
#     generator1=train_generator1,
#     generator2=train_generator2,
#     img_size=(120),
#     batch_size=batch,
# )
# Found 72000 images belonging to 1 classes.
test_data = test_gen.flow_from_directory(
    'C:/workspace/lotte/test_new',
    target_size = (120, 120),
    class_mode = None,
    batch_size = batch,
    shuffle = False
)

#2. 모델
#2. 모델
eff = EfficientNetB7(include_top = False, input_shape=(120 ,120, 3))
eff.trainable = False

a = eff.output
a = GlobalAveragePooling2D() (a)
a = Flatten() (a)
a = Dense(4048, activation= 'swish') (a)
a = Dropout(0.2) (a)
a = Dense(1000, activation= 'softmax') (a)

model = Model(inputs = eff.input, outputs = a)
#3. 컴파일 훈련
model.compile(loss = 'sparse_categorical_crossentropy', optimizer = 'adam', metrics = ['sparse_categorical_accuracy'])
model.fit(train_data, steps_per_epoch = np.ceil(39000/batch), validation_steps= np.ceil(9000/batch),\
    epochs = epochs, callbacks = [es, cp, lr])

model = load_model(model_path)

#4. 평가 예측
result = []

for tta in range(50):
    print(f'{tta+1} 번째 TTA 진행중')
    pred = model.predict(test_data, steps = len(test_data))
    pred = np.argmax(pred, 1)
    result.append(pred)
    print(f'{tta+1} 번째 제출 파일 저장하는 중')
    temp = np.array(result)
    temp = np.transpose(result)
    temp_mode = stats.mode(temp, axis = 1).mode
    sub.loc[:, 'prediction'] = temp_mode
    sub.to_csv(save_folder + '/sample1_{0:03}_{1:02}.csv'.format(filenum, (tta+1)), index = False)
    temp_count = stats.mode(temp, axis = 1).count
    for i, count in enumerate(temp_count):
        if count < tta/2.:
            print(f'{tta+1} 반복 중 {i} 번째는 횟수가 {count} 로 {(tta+1)/2.} 미만!')

cumsum = 0
for tta in range(50):
    print(f'{tta+1} 번째 TTA 진행중')
    pred = model.predict(test_data, steps = len(test_data)) # (72000, 1000)
    
    cumsum += pred
    temp = cumsum / (tta+1)
    temp_sub = np.argmax(temp, 1)
    temp_percent = np.max(temp, 1)
    
    count = 0
    print(f'TTA {tta} : {count} 개가 불확실!')
    i = 0
    for percent in temp_percent:
        count = 0
        if percent < 0.5:
            print(f'{i} 번째 테스트 이미지는 {percent}% 의 정확도를 가짐')
            count += 1
        i += 1
    print(f'{tta+1} ')
    print(f'{tta+1} 번째 제출 파일 저장하는 중')
    sub.loc[:, 'prediction'] = temp_sub
    sub.to_csv(save_folder + '/sample_final_{0:03}_{1:02}.csv'.format(filenum, (tta+1)), index = False)