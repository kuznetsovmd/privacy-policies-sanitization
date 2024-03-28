import os
import shutil
import torch
from torch import device as get_device
from torch.cuda import current_device, is_available


def select_device(use_cuda):
    d = current_device() if is_available() and use_cuda else get_device('cpu')
    print(f'Torch version: {torch.__version__}')
    try:
        print(f'Using: {torch.cuda.get_device_name(d)}')
    except ValueError:
        print(f'Using: CPU')
    return d


def build_model(path, wrapper, module, module_parameters, optimizer, optimizer_parameters, 
                criterion, criterion_parameters, name, version, pretrained):
    model = wrapper()
    model.module = module(**module_parameters)
    model.optimizer = optimizer(model.module.parameters(), **optimizer_parameters)
    model.criterion = criterion(**criterion_parameters)

    model.name = name
    model.version = version
    model.path = path

    if pretrained:
        loaded = torch.load(f'{path}/{name}.{version}.pt')

        if loaded:
            model.module.load_state_dict(loaded['model_state_dict'])
            model.optimizer.load_state_dict(loaded['optimizer_state_dict'])
            model.last_epoch = loaded['last_epoch']
            model.train_losses = loaded['train_losses']
            model.validation_losses = loaded['validation_losses']
            model.train_accuracies = loaded['train_accuracies']
            model.validation_accuracies = loaded['validation_accuracies']

    else:
        shutil.rmtree(path, ignore_errors=True)

    return model


def save_model(model, path):
    os.makedirs(path, exist_ok=True)
    torch.save({
        'last_epoch': model.last_epoch,
        'model_state_dict': model.module.state_dict(),
        'optimizer_state_dict': model.optimizer.state_dict(),
        'train_losses': model.train_losses,
        'validation_losses': model.validation_losses,
        'train_accuracies': model.train_accuracies,
        'validation_accuracies': model.validation_accuracies,
    }, f'{path}/{model.name}.{model.version}.pt')
    