import torch

from config import *

DEVICE = torch.device('cpu')
if torch.cuda.is_available() and USE_CUDA:
    DEVICE = torch.cuda.current_device()
