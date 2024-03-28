
import os
import random
import time

import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from utils.data import DocsDataset, doc_to_tensor, predicted_to_label
from utils.models import build_model, save_model
from utils.fsys import list_files, read_lines
from utils.timing import time_since


def train_filter(input_true, input_false, n_epochs, train_split, model_conf, model_path):

    yes = [('Yes', read_lines(f)) for f in list_files(input_true)]
    no = [('No', read_lines(f)) for f in list_files(input_false)]

    # BALANCING DATA
    while len(no) < len(yes):
        no.append(random.choice(no))

    train_length = int(len(no) * train_split)
    train_data = DocsDataset(yes[:train_length], no[:train_length])
    validation_data = DocsDataset(yes[train_length:], no[train_length:])

    # MAKING LOADER
    train_loader = DataLoader(train_data, shuffle=True, batch_size=1)
    validation_loader = DataLoader(validation_data, shuffle=True, batch_size=1)

    rnn = build_model(model_path, **model_conf)

    current_epoch = 0
    start = time.time()
    for epoch in range(current_epoch, n_epochs):

        # TRAINING
        for it, (label_tensor, sample_tensor) in tqdm(enumerate(train_loader, 1), 
                                                      desc="T", ascii=True, total=len(train_data)):
            rnn.train(label_tensor[0], sample_tensor[0])

        # VALIDATION
        for it, (label_tensor, sample_tensor) in tqdm(enumerate(validation_loader, 1), 
                                                      desc="V", ascii=True, total=len(validation_data)):
            rnn.test(label_tensor[0], sample_tensor[0])

        rnn.epoch()
        rnn.version = epoch
        save_model(rnn, model_path)

        print(f'R: epoch={epoch} [{epoch * 100 // n_epochs}%] time=[{time_since(start)}] '
              f'T loss={rnn.train_losses[-1]:.3f} V loss={rnn.validation_losses[-1]:.3f}, '
              f'T accuracy={rnn.train_accuracies[-1]:.3f} V accuracy={rnn.validation_accuracies[-1]:.3f}\n')


def eval_filter(model_path, input_docs, model_conf, output_true, output_false):
    all_docs = [(os.path.basename(f), read_lines(f)) for f in list_files(input_docs)]

    rnn = build_model(model_path, **model_conf)

    with torch.no_grad():
        
        for it, (save, sample) in tqdm(enumerate(all_docs, 1), ascii=True, total=len(all_docs)):
            if predicted_to_label(rnn.predict(doc_to_tensor(sample))) == 'Yes':
                with open(f'{output_true}/{save}', 'w') as f:
                    f.write(sample)
            else:
                with open(f'{output_false}/{save}', 'w') as f:
                    f.write(sample)
