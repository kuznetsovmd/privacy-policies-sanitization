from utils.fsys import make_paths


def conf(resources, tqdm_conf, **kwargs):
    inputs = {
        'input_files': f'{resources}/sanitized_html/*.md',
        'old_descriptor': f'/mnt/Source/kuznetsovmd/datasets/ppr-dataset/json/downloaded.json',
        'new_descriptor': f'{resources}/finalized/output.json',
        'old_metrics': f'/mnt/Source/kuznetsovmd/datasets/ppr-dataset/metrics.json',
        'new_metrics': f'{resources}/finalized/metrics.json',
        'statistics_file': f'{resources}/statistics.json',
        'tqdm_conf': tqdm_conf,
    }

    outputs = {
        'output_files': f'{resources}/finalized/output_policies',
    }
    make_paths(outputs.values())

    return { **inputs, **outputs }
