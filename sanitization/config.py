import torch
from torch import nn
from utils.data import N_LABELS, N_LETTERS
from filtering.models import RNN_2xR1
from sanitization.wrappers import SanitizationModel
from utils.fsys import make_paths
from utils.models import select_device


def sanitizer_training_conf(resources, use_cuda, **kwargs):
    inputs = {
        'input_docs': f'{resources}/sanitization_docs/*.txt',
        'input_labels': f'{resources}/sanitization_labels/*.txt',
        'n_epochs': 1000,
        'train_split': .8,
        'model_conf': {
            'wrapper': SanitizationModel,
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
        'model_path': f'{resources}/models/tmp_sanitization'
    }

    return { **inputs }


def sanitizer_evaluation_conf(resources, use_cuda, **kwargs):
    inputs = {
        'input_docs': f'{resources}/filtered_true/*.txt',
        'model_conf': {
            'wrapper': SanitizationModel,
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
            'version': 45,
            'pretrained': True,
        },
        'model_path': f'{resources}/models/tmp_sanitization',
    }

    outputs = {
        'sanitized_docs': f'{resources}/sanitized',
    }
    make_paths(outputs.values())

    return { **inputs, **outputs }
