from torch import nn, optim
import torch
import argparse
import torchvision
from sklearn.model_selection import KFold
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
from torch.utils.data import Dataset, DataLoader, ConcatDataset,SubsetRandomSampler
import matplotlib.pyplot as plt
import cv2
import glob
import numpy as np
import pandas as pd
import random
from tqdm import tqdm

train_data_path = '../reduced_EMNIST_DATASET/train'
valid_data_path = '../reduced_EMNIST_DATASET/val'
test_data_path = '../reduced_EMNIST_DATASET/test'

parser = argparse.ArgumentParser()
parser.add_argument('-train', '--training', default=False, type=bool, help='train model on EMNIST')
parser.add_argument('-test', '--predict', default=True, type=bool, help='test model on EMNIST')
args = parser.parse_args()

training = args.training
predict = args.predict

## train
train_image_paths = [] #to store image paths in list
classes = [] #to store class values

for data_path in glob.glob(train_data_path + '/*'):
    classes.append(data_path.split('/')[-1])
    train_image_paths.append(glob.glob(data_path + '/*'))

train_image_paths = list(np.concatenate(train_image_paths).flat)
random.shuffle(train_image_paths)

## valid
valid_image_paths = [] #to store image paths in list

for data_path in glob.glob(valid_data_path + '/*'):
    valid_image_paths.append(glob.glob(data_path + '/*'))

valid_image_paths = list(np.concatenate(valid_image_paths).flat)

## test
test_image_paths = []
for data_path in glob.glob(test_data_path + '/*'):
    test_image_paths.append(glob.glob(data_path + '/*'))

test_image_paths = list(np.concatenate(test_image_paths).flat)

#print("Train size: {}\nValid size: {}\nTest size: {}".format(len(train_image_paths), len(valid_image_paths), len(test_image_paths)))


#      Create dictionary for class indexes
idx_to_class = {i:j for i, j in enumerate(classes)}
class_to_idx = {value:key for key,value in idx_to_class.items()}

#               Define Dataset Class
class LandmarkDataset(Dataset):
    def __init__(self, image_paths, transform=False):
        self.image_paths = image_paths
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_filepath = self.image_paths[idx]
        image = cv2.imread(image_filepath)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = image.reshape((1,)+ image.shape).astype(np.float32)
        label = image_filepath.split('/')[-2]
        label = class_to_idx[label]

        return image, label

transform = torchvision.transforms.Compose([
    torchvision.transforms.ToTensor()
])

#                  Create Dataset
train_dataset = LandmarkDataset(train_image_paths, transform=transform)
valid_dataset = LandmarkDataset(valid_image_paths, transform=transform)
test_dataset = LandmarkDataset(test_image_paths, transform=transform)


train_dataset.transform = transform
valid_dataset.transform = transform
test_dataset.transform = transform


# model
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

loss_func = nn.CrossEntropyLoss()

# training
device = 'cpu'
num_epochs = 10
criterion = nn.CrossEntropyLoss()
dataset = ConcatDataset([train_dataset, valid_dataset])
batch_size = 128
k = 4
splits = KFold(n_splits=k,shuffle=True,random_state=42)
foldperf = {}

def train_epoch(model,device,dataloader,loss_fn,optimizer):
    train_loss,train_correct=0.0,0
    model.train()
    for images, labels in dataloader:

        images,labels = images.to(device),labels.to(device)
        optimizer.zero_grad()
        output, _ = model(images)
        loss = loss_fn(output,labels)
        loss.backward()
        optimizer.step()
        train_loss += loss.item() * images.size(0)
        scores, predictions = torch.max(output.data, 1)
        train_correct += (predictions == labels).sum().item()

    return train_loss,train_correct

def valid_epoch(model,device,dataloader,loss_fn):
    valid_loss, val_correct = 0.0, 0
    model.eval()
    for images, labels in dataloader:

        images,labels = images.to(device),labels.to(device)
        output, _ = model(images)
        loss=loss_fn(output,labels)
        valid_loss+=loss.item()*images.size(0)
        scores, predictions = torch.max(output.data,1)
        val_correct+=(predictions == labels).sum().item()

    return valid_loss,val_correct


if training:
    for fold, (train_idx,val_idx) in enumerate(splits.split(np.arange(len(dataset)))):

        print('Fold {}'.format(fold + 1))

        train_sampler = SubsetRandomSampler(train_idx)
        test_sampler = SubsetRandomSampler(val_idx)
        train_loader = DataLoader(dataset, batch_size=batch_size, sampler=train_sampler)
        test_loader = DataLoader(dataset, batch_size=batch_size, sampler=test_sampler)

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        model = CNN()
        model.to(device)
        optimizer = optim.Adam(model.parameters(), lr=0.002)

        history = {'train_loss': [], 'test_loss': [],'train_acc':[],'test_acc':[]}

        for epoch in range(num_epochs):
            train_loss, train_correct=train_epoch(model,device,train_loader,criterion,optimizer)
            test_loss, test_correct=valid_epoch(model,device,test_loader,criterion)

            train_loss = train_loss / len(train_loader.sampler)
            train_acc = train_correct / len(train_loader.sampler) * 100
            test_loss = test_loss / len(test_loader.sampler)
            test_acc = test_correct / len(test_loader.sampler) * 100

            print("Epoch:{}/{} |\
                train_loss:{:.3f} |\
                val_loss:{:.3f} |\
                train_acc {:.2f}% |\
                test_acc {:.2f}%".format(epoch + 1,
                                        num_epochs,
                                        train_loss,
                                        test_loss,
                                        train_acc,
                                        test_acc))
            history['train_loss'].append(train_loss)
            history['test_loss'].append(test_loss)
            history['train_acc'].append(train_acc)
            history['test_acc'].append(test_acc)

        foldperf['fold{}'.format(fold+1)] = history

    torch.save(model,'CNN.pt')

if predict:
    y_pred_list = []
    y_test = []
    model_path = 'CNN.pt'
    with torch.no_grad():
        model = torch.load(model_path)
        model.eval()
        dataloader = DataLoader(test_dataset, batch_size=batch_size)
        for X_batch, y_batch in dataloader:
            X_batch = X_batch.to(device)
            y_test_pred, _ = model(X_batch)
            _, y_pred_tags = torch.max(y_test_pred, dim = 1)
            y_pred_list.append(y_pred_tags.cpu().numpy())
            y_test.append(y_batch.cpu().numpy())

    y_pred_list = [idx_to_class[x] for xs in y_pred_list for x in xs]
    y_test = [idx_to_class[x] for xs in y_test for x in xs]

    report = classification_report(y_test, y_pred_list, output_dict=True)
    #print(report)
    df = pd.DataFrame(report).transpose()
    df.to_excel('classification_report.xlsx')
    ConfusionMatrixDisplay.from_predictions(y_test, y_pred_list, include_values=False)
    plt.savefig('confusion_matrix.png')
