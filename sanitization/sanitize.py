
import os
import time
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
from utils.data import ParagraphsDataset, doc_to_tensor, predicted_to_label
from utils.models import build_model, save_model
from utils.fsys import list_files, read_lines
from utils.timing import time_since


def train_sanitizer(input_docs, input_labels, n_epochs, train_split, model_conf, model_path):
    texts = [read_lines(f) for f in sorted(list_files(input_docs))]
    labels = [read_lines(f) for f in sorted(list_files(input_labels))]

    # BALANCING DATA
    train_length = int(len(texts) * train_split)
    train_data = ParagraphsDataset(labels[:train_length], texts[:train_length])
    validation_data = ParagraphsDataset(labels[train_length:], texts[train_length:])

    # MAKING LOADER
    train_loader = DataLoader(train_data, shuffle=False, batch_size=1)
    validation_loader = DataLoader(validation_data, shuffle=False, batch_size=1)

    rnn = build_model(model_path, **model_conf)

    current_epoch = 0
    start = time.time()
    for epoch in range(current_epoch, n_epochs):
        # TRAINING
        for it, (label_tensor, sample_tensor) in tqdm(enumerate(train_loader, 1), desc="T", ascii=True, total=len(train_data)):
            rnn.train(label_tensor[0], sample_tensor[0])

        # VALIDATION
        for it, (label_tensor, sample_tensor) in tqdm(enumerate(validation_loader, 1), desc="V", ascii=True, total=len(validation_data)):
            rnn.test(label_tensor[0], sample_tensor[0])

        rnn.epoch()
        rnn.version = epoch
        save_model(rnn, model_path)

        print(f'R: epoch={epoch} [{epoch * 100 // n_epochs}%] time=[{time_since(start)}] '
              f'T loss={rnn.train_losses[-1]:.3f} V loss={rnn.validation_losses[-1]:.3f}, '
              f'T accuracy={rnn.train_accuracies[-1]:.3f} V accuracy={rnn.validation_accuracies[-1]:.3f}\n')


def eval_sanitizer(input_docs, model_conf, model_path, sanitized_docs):
    all_docs = [(os.path.basename(f), read_lines(f)) for f in list_files(input_docs)]

    rnn = build_model(model_path, **model_conf)

    with torch.no_grad():
        for it, (save, sample) in tqdm(enumerate(all_docs, 1), ascii=True, total=len(all_docs)):
            output = rnn.predict(doc_to_tensor(sample))
            predicted_label = list(zip([predicted_to_label(o) for o in output], sample.split('\n\n\n')))

            with open(f'{sanitized_docs}/{save}', 'w') as f:
                for i, (l, s) in enumerate(predicted_label):
                    if l == 'Yes':
                        f.write(f'\n\n\n{s}')