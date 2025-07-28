import os


def env():
    resources = 'resources'
    os.makedirs(resources, exist_ok=True)

    return {
        'use_cuda': True,
        'resources': resources,
        'tqdm_conf': {
            'ncols': 80
        }
    }
