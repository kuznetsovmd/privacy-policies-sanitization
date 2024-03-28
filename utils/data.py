import torch

from torch.utils.data.dataset import Dataset

from env import env
from utils.models import select_device


ENV = env()
DEVICE = select_device(ENV['use_cuda'])


digits = ''.join([chr(ord('0') + i) for i in range(10)])
ru_letters = ''.join([chr(ord('а') + i) for i in range(32)])
en_letters = ''.join([chr(ord('a') + i) for i in range(26)])
spec_chars = ''.join(' .,:;!?\"\'/\\*-{}()[]\n')
all_letters = f'{spec_chars}{digits}{ru_letters}ё{ru_letters.upper()}Ё{en_letters}{en_letters.upper()}'
N_LETTERS = len(all_letters)

letter2index = {c: i for i, c in enumerate(all_letters)}
index2letter = {i: c for i, c in enumerate(all_letters)}

all_labels = ['Yes', 'No']
N_LABELS = len(all_labels)

label2index = {c: i for i, c in enumerate(all_labels)}
index2label = {i: c for i, c in enumerate(all_labels)}

letters = torch.nn.functional.one_hot(torch.arange(N_LETTERS).view(N_LETTERS, -1)).to(DEVICE)
labels = torch.tensor([0, 1]).view(2, -1).to(DEVICE)


def letter_to_tensor(letter):
    return torch.clone(letters[letter2index[letter]])


def line_to_tensor(line):
    tensor = torch.zeros(len(line), 1, N_LETTERS, device=DEVICE)
    for i, letter in enumerate(line):
        tensor[i, 0, :] = letter_to_tensor(letter)
    return tensor


def label_to_tensor(label):
    return torch.clone(labels[label2index[label]])


def labels_to_tensors(labels):
    labels = labels.split('\n')
    tensor = torch.empty(len(labels), 1, dtype=torch.long, device=DEVICE)
    for i, label in enumerate(labels):
        tensor[i, :] = label_to_tensor(label)
    return tensor


def predicted_to_label(predicted):
    _, top_i = predicted.topk(1)
    return index2label[top_i.item()]


def paragraph_to_tensor(string):
    return torch.tensor([string.count(i) for i in all_letters])


def doc_to_tensor(doc):
    paragraphs = doc.split('\n\n\n')
    tensor = torch.empty(len(paragraphs), 1, N_LETTERS, device=DEVICE)
    for i, paragraph in enumerate(paragraphs):
        tensor[i, 0, :] = paragraph_to_tensor(paragraph)
    return tensor


class DocsDataset(Dataset):
    def __init__(self, c1, c2):
        self.samples = [c1, c2]

    def __len__(self):
        return len(self.samples[0]) + len(self.samples[1])

    def __getitem__(self, idx):
        label, sample = self.samples[idx % 2][idx // 2]
        return label_to_tensor(label), doc_to_tensor(sample)


class ParagraphsDataset(Dataset):
    def __init__(self, labels, samples):
        self.samples = [labels, samples]

    def __len__(self):
        return len(self.samples[1])

    def __getitem__(self, idx):
        return labels_to_tensors(self.samples[0][idx]), doc_to_tensor(self.samples[1][idx])