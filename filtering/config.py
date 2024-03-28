import torch
from torch import nn
from utils.data import N_LABELS, N_LETTERS
from filtering.models import RNN_2xR1
from filtering.wrappers import FilterModel
from utils.fsys import make_paths
from utils.models import select_device


def filter_training_conf(resources, use_cuda, **kwargs):
    inputs = {
        'input_true': f'{resources}/filtering_true/*.txt',
        'input_false': f'{resources}/filtering_false/*.txt',
        'n_epochs': 1000,
        'train_split': .8,
        'model_conf': {
            'wrapper': FilterModel,
            'module': RNN_2xR1,
            'module_parameters': {
                'input_size': N_LETTERS,
                'hidden_size': 512,
                'output_size': N_LABELS,
                'dropout': .1,
                'device': select_device(use_cuda),
            },
            'optimizer': torch.optim.Adam,
            'optimizer_parameters': {
                'lr':  1e-7,
                'eps': 1e-10,
            },
            'criterion': nn.CrossEntropyLoss,
            'criterion_parameters': {},
            'name': 'rnn-filter',
            'version': 0,
            'pretrained': False,
        },
        'model_path': f'{resources}/models/tmp_filtering'
    }

    return { **inputs }


def filter_evaluation_conf(resources, use_cuda, **kwargs):
    inputs = {
        'input_docs': '/mnt/Source/kuznetsovmd/__datasets/ru/output_policies/*.txt',
        'model_conf': {
            'wrapper': FilterModel,
            'module': RNN_2xR1,
            'module_parameters': {
                'input_size': N_LETTERS,
                'hidden_size': 512,
                'output_size': N_LABELS,
                'dropout': .1,
                'device': select_device(use_cuda),
            },
            'optimizer': torch.optim.Adam,
            'optimizer_parameters': {
                'lr':  1e-7,
                'eps': 1e-10,
            },
            'criterion': nn.CrossEntropyLoss,
            'criterion_parameters': {},
            'name': 'rnn-filter',
            'version': 10,
            'pretrained': True,
        },
        'model_path': f'{resources}/models/filtering',
    }

    outputs = {
        'output_true': f'{resources}/tmp_filtered_true',
        'output_false': f'{resources}/tmp_filtered_false',
    }
    make_paths(outputs.values())

    return { **inputs, **outputs }
