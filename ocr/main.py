#import warnings
#warnings.filterwarnings("ignore")

import cv2
import torch
import pandas as pd
import numpy as np
from torch import nn
from PIL import Image,ImageOps
import segmentor as segmentor
import matplotlib.pyplot as plt
import os
import shutil

# 'segmented' directory contains each mathematical symbol in the image
root = os.getcwd()
if 'segmented' in os.listdir():
    shutil.rmtree('segmented')
os.mkdir('segmented')
SEGMENTED_OUTPUT_DIR = os.path.join(root, 'segmented')
# trained model
MODEL_PATH = os.path.join(root, 'CNN.pt')
print(f'### model path: {MODEL_PATH}')
# csv file that maps numerical code to the character
mapping_processed = os.path.join(root, 'full_mapper.csv')

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(
                in_channels=1,
                out_channels=16,
                kernel_size=5,
                stride=1,
                padding=2,
            ),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, 5, 1, 2),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(32, 64, 5, 1, 2),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.drop1=nn.Dropout2d(p=0.5)
        # fully connected layers, output 78 classes
        self.output = nn.Sequential(
            nn.Linear(64 * 5 * 5, 120),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(120, 78)
        )

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x=self.drop1(x)
        x = x.view(x.size(0), -1)
        output = self.output(x)
        return output, x    # return x for visualization

def img2emnist(filepath, char_code):
    """
    Prende l'immagine (segmentata direi), fa sharpening e la associa al char corrispondente (da dove arriva e com'è fatto?)
    """
    img = Image.open(filepath).resize((45, 45))
    inv_img = ImageOps.invert(img)
    flatten = np.array(inv_img).flatten() / 255
    flatten = np.where(flatten > 0.5, 1, 0)
    csv_img = ','.join([str(num) for num in flatten])
    csv_str = '{},{}'.format(char_code, csv_img)
    return csv_str

def processor(INPUT_IMAGE):
    img = Image.open(INPUT_IMAGE)
    # segmenting each character in the image
    segmentor.image_segmentation(INPUT_IMAGE)
    segmented_images = []
    files = sorted(list(os.walk(SEGMENTED_OUTPUT_DIR))[0][2])
    # writing images to the 'segmented' directory
    for file in files:
        file_path = os.path.join(SEGMENTED_OUTPUT_DIR , file)
        segmented_images.append(Image.open(file_path))

    files = sorted(list(os.walk(SEGMENTED_OUTPUT_DIR))[0][2])
    for file in files:
        filename = os.path.join(SEGMENTED_OUTPUT_DIR, file)
        img = cv2.imread(filename, 0)

        kernel = np.ones((2,2), np.uint8)
        dilation = cv2.erode(img, kernel, iterations = 1)
        cv2.imwrite(filename, dilation)

    segmented_characters = 'segmented_characters.csv'
    if segmented_characters in os.listdir():
        os.remove(segmented_characters)
    # resize image to 48x48 and write the flattened out list to the csv file
    with open(segmented_characters, 'a+') as f_test:
        column_names = ','.join(["label"] + ["pixel" + str(i) for i in range(2025)])
        print(column_names, file=f_test)

        files = sorted(list(os.walk(SEGMENTED_OUTPUT_DIR))[0][2])
        for f in files:
            file_path = os.path.join(SEGMENTED_OUTPUT_DIR, f)
            csv = img2emnist(file_path, -1)
            print(csv, file=f_test)

    data = pd.read_csv('segmented_characters.csv')
    X_data = data.drop('label', axis = 1)
    #print(X_data.shape)
    X_data = X_data.values.reshape(-1,1,45,45)
    X_data = X_data.astype(float)
    X_data = torch.from_numpy(X_data).float()
    for n in range(8):
        print(torch.equal(X_data[n], X_data[n+1]))
    X_data = X_data[4:6]
    #print(X_data.shape, X_data)

    df = pd.read_csv(mapping_processed)
    code2char = {}
    for index, row in df.iterrows():
        code2char[index] = row['char']
    # predict each segmented character
    with torch.no_grad():
        model = CNN()
        model = torch.load(MODEL_PATH)
        model.eval()
        results, _ = model(X_data)
    print(results)
    _, results = torch.max(results, dim = 1)
    print(results)
    parsed_str = ""
    for r in results.cpu().numpy():
        parsed_str += code2char[r]
    return parsed_str

def main(operationBytes):
    Image.open(operationBytes).save('input.png')
    equation = processor('input.png')
    print('\nequation :', equation)
    return equation
