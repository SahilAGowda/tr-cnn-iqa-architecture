import torch
from dataset import KadidDataset
from torchvision.transforms import ToTensor
from models.vit import ViT
from models.cnn import CNN
from models.trcnn import TrCNN
from torch.utils.data import DataLoader
from tqdm import tqdm
from utils import rgb_to_grayscale
import torch.optim as optim
import torch.nn as nn
import os

VIT_MODEL_PATH = "vit.pth"
CNN_MODEL_PATH = "cnn.pth"
BATCH_SIZE=50

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print(f"Device: {device}")

def test(vit, cnn, loader, device='cpu'):
  accuracy = 0
  with torch.no_grad():
    for batch in tqdm(loader, desc='Testing'):
      x, y = batch

      x = rgb_to_grayscale(x).unsqueeze(1) 
      y = y.reshape(-1, 1).float()
      x, y = x.to(device), y.to(device)

      # y_hat = trcnn(x)
      # y_hat = vit(cnn(x))

      print(y_hat)

      accuracy += 1 - torch.sigmoid(y_hat - y).abs().mean()
      torch.cuda.empty_cache()

    accuracy = accuracy / len(loader)

    return accuracy


data = KadidDataset(
  csv_file="data/kadid10k/dmos.csv",
  root_dir="data/kadid10k/images",
  transform=ToTensor()
)

loader = DataLoader(data, batch_size=BATCH_SIZE, shuffle=True, num_workers=1)

cnn = CNN(
  diffusion_x=100, 
  diffusion_y=100
).to(device)

vit = ViT(
  channel=1, 
  height=100, 
  width=100, 
  n_patches=10, 
  n_blocks=2, 
  hidden_d=8, 
  n_heads=2, 
  out_d=1
).to(device)

cnn.load_state_dict(torch.load(CNN_MODEL_PATH))
vit.load_state_dict(torch.load(VIT_MODEL_PATH))

trcnn = TrCNN(cnn, vit).to(device)

if __name__ == '__main__':
  accuracy = test(vit, cnn, loader, device)
  print(f"Accuracy: {accuracy}")

  torch.cuda.empty_cache()