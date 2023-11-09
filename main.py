import sys
import random
import time
import math

import torch
import torch.nn as nn

from functools import wraps
from torch.utils.data.dataloader import DataLoader
from tqdm import tqdm

from models import *
from docs import *
from config import *
from fetch_device import *


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper


def time_since(since):
    now = time.time()
    s = now - since
    m = math.floor(s / 60)
    s -= m * 60
    return '%dm %ds' % (m, s)


def train_filter():

    yes = [('Yes', read_lines(f)) for f in find_files(f'{TRAINING_DATA}/filtering/yes/*.txt')]
    no = [('No', read_lines(f)) for f in find_files(f'{TRAINING_DATA}/filtering/no/*.txt')]

    while len(no) < len(yes):
        no.append(random.choice(no))

    train_data = DocsDataset(yes[:800], no[:800])
    validation_data = DocsDataset(yes[800:1000], no[800:1000])

    # BUSINESS
    train_loader = DataLoader(train_data, shuffle=True, batch_size=1)
    validation_loader = DataLoader(validation_data, shuffle=True, batch_size=1)

    parameters = {
        'module': RNN_2xR1,
        'module_parameters': {
            'input_size': n_letters,
            'hidden_size': 512,
            'output_size': n_labels,
            'dropout': .1,
            'device': DEVICE,
        },
        'optimizer': torch.optim.Adam,
        'optimizer_parameters': {
            'lr':  1e-7,
            'eps': 1e-10,
        },
        'criterion': nn.CrossEntropyLoss,
        'criterion_parameters': {},
        'pretrained': True,
        'path': f'{RESOURCES}/models/rnn9/model_182_470',
    }

    rnn = build_model(**parameters)

    n_epochs = 1000
    current_epoch = 0

    start = time.time()

    for epoch in range(current_epoch, n_epochs):

        # TRAINING
        for it, (label_tensor, sample_tensor) in tqdm(enumerate(train_loader, 1), desc="T", ascii=True, total=len(train_data)):
            rnn.train(label_tensor[0], sample_tensor[0])

        # VALIDATION
        for it, (label_tensor, sample_tensor) in tqdm(enumerate(validation_loader, 1), desc="V", ascii=True, total=len(validation_data)):
            rnn.test(label_tensor[0], sample_tensor[0])

        rnn.epoch()
        save_model(rnn, f'{epoch}')

        print(f'R: epoch={epoch} [{epoch * 100 // n_epochs}%] time=[{time_since(start)}] '
              f'T loss={rnn.train_losses[-1]:.3f} V loss={rnn.validation_losses[-1]:.3f}, '
              f'T accuracy={rnn.train_accuracies[-1]:.3f} V accuracy={rnn.validation_accuracies[-1]:.3f}\n')

    return 0

def eval_filter():
    all_docs = [(os.path.basename(f), read_lines(f)) for f in find_files(f'{VALIDATION_DATA}/plain_policies/*.txt')]

    parameters = {
        'module': RNN_2xR1,
        'module_parameters': {
            'input_size': n_letters,
            'hidden_size': 512,
            'output_size': n_labels,
            'device': DEVICE,
        },
        'optimizer': torch.optim.Adam,
        'optimizer_parameters': {
            'lr':  1e-6,
            'eps': 1e-6,
        },
        'criterion': nn.CrossEntropyLoss,
        'criterion_parameters': {},
        'pretrained': True,
        'path': f'{RESOURCES}/models/rnn9/model_182_470_60',
    }

    rnn = build_model(**parameters)

    with torch.no_grad():
        
        for it, (save, sample) in tqdm(enumerate(all_docs, 1), ascii=True, total=len(all_docs)):
            if predicted_to_label(rnn.predict(doc_to_tensor(sample))) == 'Yes':
                with open(f'{RESOURCES}/filtered_policies/yes/{save}', 'w') as f:
                    f.write(sample)
            else:
                with open(f'{RESOURCES}/filtered_policies/no/{save}', 'w') as f:
                    f.write(sample)

def train_sanitize():
    texts = [read_lines(f) for f in sorted(find_files(f'{RESOURCES}/sanitization_docs/*.txt'))]
    labels_ = [read_lines(f) for f in sorted(find_files(f'{RESOURCES}/sanitization_labels/*.txt'))]

    train_length = int(len(texts) * 0.95)

    train_data = ParagraphsDataset(labels_[:train_length], texts[:train_length])
    validation_data = ParagraphsDataset(labels_[train_length:], texts[train_length:])

    # BUSINESS
    train_loader = DataLoader(train_data, shuffle=False, batch_size=1)
    validation_loader = DataLoader(validation_data, shuffle=False, batch_size=1)

    parameters = {
        'module': RNN_2xR1,
        'module_parameters': {
            'input_size': n_letters,
            'hidden_size': 512,
            'output_size': n_labels,
            'dropout': .1,
            'device': DEVICE,
        },
        'optimizer': torch.optim.Adam,
        'optimizer_parameters': {
            'lr':  1e-7,
            'eps': 1e-10,
        },
        'criterion': nn.CrossEntropyLoss,
        'criterion_parameters': {},
        'pretrained': False,
        'path': f'{RESOURCES}/models/rnn11_sanitization',
    }

    rnn = build_model(**parameters)

    n_epochs = 1000
    current_epoch = 0

    start = time.time()

    for epoch in range(current_epoch, n_epochs):

        # TRAINING
        for it, (label_tensor, sample_tensor) in tqdm(enumerate(train_loader, 1), desc="T", ascii=True, total=len(train_data)):
            rnn.train2(label_tensor[0], sample_tensor[0])

        # VALIDATION
        for it, (label_tensor, sample_tensor) in tqdm(enumerate(validation_loader, 1), desc="V", ascii=True, total=len(validation_data)):
            rnn.test2(label_tensor[0], sample_tensor[0])

        rnn.epoch()
        save_model(rnn, f'{epoch}')

        print(f'R: epoch={epoch} [{epoch * 100 // n_epochs}%] time=[{time_since(start)}] '
              f'T loss={rnn.train_losses[-1]:.3f} V loss={rnn.validation_losses[-1]:.3f}, '
              f'T accuracy={rnn.train_accuracies[-1]:.3f} V accuracy={rnn.validation_accuracies[-1]:.3f}\n')


def eval_sanitize():
    all_docs = [(os.path.basename(f), read_lines(f)) for f in find_files(f'{RESOURCES}/formatted_policies/*.txt')]

    parameters = {
        'module': RNN_2xR1,
        'module_parameters': {
            'input_size': n_letters,
            'hidden_size': 512,
            'output_size': n_labels,
            'dropout': .1,
            'device': DEVICE,
        },
        'optimizer': torch.optim.Adam,
        'optimizer_parameters': {
            'lr':  1e-7,
            'eps': 1e-10,
        },
        'criterion': nn.CrossEntropyLoss,
        'criterion_parameters': {},
        'pretrained': True,
        'path': f'{RESOURCES}/models/rnn11_sanitization_70',
    }

    rnn = build_model(**parameters)

    with torch.no_grad():
        
        for it, (save, sample) in tqdm(enumerate(all_docs, 1), ascii=True, total=len(all_docs)):
            output = rnn.predict2(doc_to_tensor(sample))
            predicted_label = list(zip([predicted_to_label(o) for o in output], sample.split('\n\n\n')))

            with open(f'{RESOURCES}/sanitized_policies/{save}', 'w') as f:
                for i, (l, s) in enumerate(predicted_label):
                    if l == 'Yes':
                        f.write(f'\n\n\n{s}')


if __name__ == '__main__':
    try:
        try:
            print(f'Using: {torch.cuda.get_device_name(DEVICE)}')
        except ValueError:
            print(f'Using: CPU')
        sys.exit(eval_sanitize())
    except KeyboardInterrupt:
        print('Interrupted by user')
        sys.exit(130)
    except NAN as e:
        print(e)
        sys.exit(1)

