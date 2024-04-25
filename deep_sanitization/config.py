import torch
from torch import nn
from deep_sanitization.rnn_simple import RNN_2xR1
from deep_sanitization.rnn_simple import SanitizationModel
from utils.fsys import make_paths
from utils.model import select_device


def sanitizer_training_conf(resources, use_cuda, **kwargs):
    device = select_device(use_cuda)

    inputs = {
        'input_docs': f'{resources}/annotations/direct_sanitization_docs/*.txt',
        'input_labels': f'{resources}/annotations/direct_sanitization_labels/*.txt',
        'n_epochs': 1000,
        'train_split': .8,
        'model_conf': {
            'wrapper': SanitizationModel,
            'module': RNN_2xR1,
            'device': device,
            'module_parameters': {
                'input_size': SanitizationModel.N_LETTERS,
                'hidden_size': 512,
                'output_size': SanitizationModel.N_LABELS,
                'dropout': .1,
                'device': device,
            },
            'optimizer': torch.optim.AdamW,
            'optimizer_parameters': {
                'lr':  1e-5,
                'eps': 1e-9,
            },
            'criterion': nn.CrossEntropyLoss,
            'criterion_parameters': {
                'label_smoothing': .1,
            },
            'name': 'rnn-filter',
            'version': 0,
            'pretrained': False,
        },
        'model_path': f'{resources}/models/direct_sanitization',
        'tqdm_conf': {
            'ncols': 80,
        }
    }

    return { **inputs }


def sanitizer_evaluation_conf(resources, use_cuda, **kwargs):
    device = select_device(use_cuda)
    
    inputs = {
        'input_docs': f'{resources}/normalized/*.txt',
        'model_conf': {
            'wrapper': SanitizationModel,
            'module': RNN_2xR1,
            'device': device,
            'module_parameters': {
                'input_size': SanitizationModel.N_LETTERS,
                'hidden_size': 512,
                'output_size': SanitizationModel.N_LABELS,
                'dropout': .1,
                'device': device,
            },
            'optimizer': torch.optim.AdamW,
            'optimizer_parameters': {
                'lr':  1e-5,
                'eps': 1e-9,
            },
            'criterion': nn.CrossEntropyLoss,
            'criterion_parameters': {
                'label_smoothing': .1,
            },
            'name': 'rnn-filter',
            'version': 339,
            'pretrained': True,
        },
        'model_path': f'{resources}/models/direct_sanitization',
        'tqdm_conf': {
            'ncols': 80,
        }
    }

    outputs = {
        'sanitized_docs': f'{resources}/sanitized',
    }
    make_paths(outputs.values())

    return { **inputs, **outputs }
