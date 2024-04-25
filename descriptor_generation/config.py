from utils.fsys import make_paths


def normalizer_conf(resources, **kwargs):
    inputs = {
        'input_files': f'/mnt/Source/kuznetsovmd/__datasets/ru_dirty/plain_policies/*.txt',
        'old_descriptor': f'/mnt/Source/kuznetsovmd/__datasets/ru_dirty/json/plain.json',
        'new_descriptor': f'{resources}/finalized/output.json',
    }

    outputs = {
        'output_files': f'{resources}/finalized/output_policies',
    }
    make_paths(outputs.values())

    return { **inputs, **outputs }
