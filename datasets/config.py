from utils.fsys import make_paths


def filtering_conf(resources, **kwargs):
    inputs = {
        'editor': 'less',
        'input_docs': '/mnt/Source/kuznetsovmd/__datasets/ru/output_policies'
    }

    outputs = {
        'output_true': f'{resources}/tmp_filtering_true',
        'output_false': f'{resources}/tmp_filtering_false'
    }
    make_paths(outputs.values())

    return { **inputs, **outputs }


def sanitization_conf(resources, **kwargs):
    inputs = {
        'input_docs': f'{resources}/tmp_filtering_true'
    }

    outputs = {
        'output_docs': f'{resources}/tmp_sanitization_docs',
        'output_labels': f'{resources}/tmp_sanitization_labels'
    }
    make_paths(outputs.values())

    return { **inputs, **outputs }
