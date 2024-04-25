import os
import shutil
import torch
from torch import device as get_device
from torch.cuda import current_device, is_available

from utils.timing import time_since


def print_stats(epoch, n_epochs, start, stats):
        print(f'R: epoch={epoch} [{epoch * 100 // n_epochs}%] time=[{time_since(start)}] '
              f'T loss={stats["t_loss"]:.3f}, T accuracy={stats["t_accuracy"]:.3f} '
              f'V loss={stats["v_loss"]:.3f}, V accuracy={stats["v_accuracy"]:.3f}\n')


def select_device(use_cuda):
    d = current_device() if is_available() and use_cuda else get_device('cpu')
    print(f'Torch version: {torch.__version__}')
    try:
        print(f'Using: {torch.cuda.get_device_name(d)}')
    except ValueError:
        print(f'Using: CPU')
    return d


def build_model(path, wrapper, module, device, module_parameters, optimizer, optimizer_parameters, 
                criterion, criterion_parameters, name, version, pretrained):
    model = wrapper()
    model.device = device
    model.module = module(**module_parameters)
    model.optimizer = optimizer(model.module.parameters(), **optimizer_parameters)
    model.criterion = criterion(**criterion_parameters)

    model.name = name
    model.version = version
    model.path = path

    if pretrained:
        loaded = torch.load(f'{path}/{name}.{version:010d}.pt')

        if loaded:
            model.name = loaded['name']
            model.version = loaded['version']
            model.module.load_state_dict(loaded['model_state_dict'])
            model.optimizer.load_state_dict(loaded['optimizer_state_dict'])
            model.stats_mem = loaded['stats_mem']

    else:
        shutil.rmtree(path, ignore_errors=True)

    return model


def save_model(model, path):
    os.makedirs(path, exist_ok=True)
    torch.save({
        'name': model.name,
        'version': model.version,
        'model_state_dict': model.module.state_dict(),
        'optimizer_state_dict': model.optimizer.state_dict(),
        'stats_mem': model.stats_mem,
    }, f'{path}/{model.name}.{model.version:010d}.pt')
