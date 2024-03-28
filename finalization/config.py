from utils.fsys import make_paths


def finalizer_conf(resources, **kwargs):
    inputs = {
        'input_files': f'{resources}/sanitized/*.txt',
        'old_descriptor': f'/mnt/Source/kuznetsovmd/__datasets/ru/output.json',
        'new_descriptor': f'{resources}/finalized/output.json',
    }

    outputs = {
        'output_files': f'{resources}/finalized/output_policies',
    }
    make_paths(outputs.values())

    return { **inputs, **outputs }
