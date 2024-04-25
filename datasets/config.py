from utils.fsys import make_paths


def dataset_conf(resources, **kwargs):
    inputs = {
        'input_docs': '/mnt/Source/kuznetsovmd/__datasets/ru/output_policies'
    }

    outputs = {
        'output_docs': f'{resources}/tmp_sanitization_docs',
        'output_labels': f'{resources}/tmp_sanitization_labels'
    }
    make_paths(outputs.values())

    return { **inputs, **outputs }
