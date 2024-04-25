
import os
import time
from tqdm import tqdm
from deep_sanitization.data import ParagraphsDataset
from utils.model import build_model, print_stats, save_model
from utils.fsys import list_files, read_lines


def train_sanitizer(input_docs, input_labels, n_epochs, train_split, model_conf, model_path, tqdm_conf):
    texts = [read_lines(f).split('\n\n\n') for f in sorted(list_files(input_docs))]
    labels = [read_lines(f).split('\n') for f in sorted(list_files(input_labels))]

    # BALANCING DATA
    train_length = int(len(texts) * train_split)
    train_data = ParagraphsDataset(texts[:train_length], labels[:train_length])
    validation_data = ParagraphsDataset(texts[train_length:], labels[train_length:])

    rnn = build_model(model_path, **model_conf)

    current_epoch = 0
    start = time.time()
    for epoch in range(current_epoch, n_epochs):
        # TRAINING
        for s, t in tqdm(train_data, desc="T", total=len(train_data), **tqdm_conf):
            rnn.train(s, t)

        # VALIDATION
        for s, t in tqdm(validation_data, desc="V", total=len(validation_data), **tqdm_conf):
            rnn.test(s, t)

        rnn.version = epoch
        save_model(rnn, model_path)
        print_stats(epoch, n_epochs, start, rnn.stats())


def eval_sanitizer(input_docs, model_conf, model_path, sanitized_docs, tqdm_conf):
    docs = [(os.path.basename(f), read_lines(f).split('\n\n\n')) for f in list_files(input_docs)]

    rnn = build_model(model_path, **model_conf)

    for _, (save, sample) in tqdm(enumerate(docs, 1), total=len(docs), **tqdm_conf):
        output = rnn.predict(sample)
        predicted_labels = list(zip([o['predicted_label'] for o in output], sample))

        with open(f'{sanitized_docs}/{save}', 'w') as f:
            for i, (l, s) in enumerate(predicted_labels):
                if l == 'Yes':
                    f.write(f'\n\n\n{s}')
                