import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F


class NAN(Exception):
    pass


class RNN_2xR1(nn.Module):
    def __init__(self, input_size=64, hidden_size=64, output_size=64, dropout=0.1, device='cpu'):
        super(RNN_2xR1, self).__init__()
        self.device = device
        self.hidden_size = hidden_size

        self.fc1 = nn.Linear(input_size + hidden_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(dropout)
        
        torch.nn.init.xavier_uniform_(self.fc1.weight)
        torch.nn.init.xavier_uniform_(self.fc2.weight)
        torch.nn.init.xavier_uniform_(self.fc3.weight)

        self.to(self.device)
        self.init_hidden()

    def forward(self, input):
        # normalized = input
        normalized = input - input.min()
        normalized = input / input.max()
        normalized = torch.cat((normalized, self.hidden), 1)

        self.hidden = F.relu(self.fc1(normalized))
        self.hidden = self.dropout(self.hidden)
        self.hidden = F.relu(self.fc2(self.hidden))
        self.hidden = self.dropout(self.hidden)
        return self.fc3(self.hidden)

    def init_hidden(self):
        self.hidden = torch.zeros(1, self.hidden_size, device=self.device)


class BaseSanitizationModel:
    digits = ''.join([chr(ord('0') + i) for i in range(10)])
    ru_letters = ''.join([chr(ord('а') + i) for i in range(32)])
    en_letters = ''.join([chr(ord('a') + i) for i in range(26)])
    spec_chars = ''.join(' .,:;!?\"\'/\\*-{}()[]\n')
    all_letters = f'{spec_chars}{digits}{ru_letters}ё{ru_letters.upper()}Ё{en_letters}{en_letters.upper()}'
    N_LETTERS = len(all_letters)

    letter2index = {c: i for i, c in enumerate(all_letters)}
    index2letter = {i: c for i, c in enumerate(all_letters)}

    all_labels = ['Yes', 'No']
    N_LABELS = len(all_labels)

    label2index = {c: i for i, c in enumerate(all_labels)}
    index2label = {i: c for i, c in enumerate(all_labels)}

    @classmethod
    def label_to_tensor(cls, label):
        return cls.label2index[label]

    @classmethod
    def labels_to_tensors(cls, labels):
        return [cls.label_to_tensor(l) for l in labels]

    @classmethod
    def predicted_to_label(cls, predicted):
        return cls.index2label[predicted]

    @classmethod
    def paragraph_to_tensor(cls, string):
        return [string.count(i) for i in cls.all_letters]

    @classmethod
    def doc_to_tensor(cls, doc):
        return [cls.paragraph_to_tensor(p) for p in doc]

    def train(self, source, target):
        src = self.doc_to_tensor(source)
        tgt = self.labels_to_tensors(target)
        l = len(src)
        assert l == len(tgt)
        
        s = torch.tensor(src, device=self.device)
        t = torch.tensor(tgt, device=self.device)

        total_loss = 0
        self.module.init_hidden()
        for i in range(l):

            output = self.module(s[i].unsqueeze(0))
            loss = self.criterion(output, t[i].unsqueeze(0))
            total_loss += loss

            predicted = torch.argmax(output, dim=1).item()
            yield {
                'predicted_label': self.predicted_to_label(predicted),
                'predicted': predicted,
                'output': output.detach().cpu().tolist()[0], 
                'loss': loss.item()
            }

        total_loss.backward()
        self.optimizer.step()
        self.optimizer.zero_grad()

    def test(self, source, target):
        src = self.doc_to_tensor(source)
        tgt = self.labels_to_tensors(target)
        l = len(src)
        assert l == len(tgt)
        
        s = torch.tensor(src, device=self.device)
        t = torch.tensor(tgt, device=self.device)

        with torch.no_grad():
            total_loss = 0
            self.module.init_hidden()
            for i in range(l):

                output = self.module(s[i].unsqueeze(0))
                loss = self.criterion(output, t[i].unsqueeze(0))
                total_loss += loss

                predicted = torch.argmax(output, dim=1).item()
                yield {
                    'predicted_label': self.predicted_to_label(predicted),
                    'predicted': predicted,
                    'output': output.detach().cpu().tolist()[0], 
                    'loss': loss.item()
                }

    def predict(self, source):
        src = self.doc_to_tensor(source)
        l = len(src)
        
        s = torch.tensor(src, device=self.device)

        with torch.no_grad():
            self.module.init_hidden()
            for i in range(l):

                output = self.module(s[i].unsqueeze(0))

                predicted = torch.argmax(output, dim=1).item()
                yield {
                    'predicted_label': self.predicted_to_label(predicted),
                    'predicted': predicted,
                    'output': output.detach().cpu().tolist()[0], 
                }


class SanitizationModel(BaseSanitizationModel):

    def __accuracy(self, output, target):
        assert len(output) == len(target), 'outputs & targets are not equal on length'
        return np.average(np.array(output) == np.array(target))
    
    def __f1score(self, output, target):
        assert len(output) == len(target), 'outputs & targets are not equal on length'
        tp = np.sum((np.array(output) == 'Yes') == (np.array(target) == 'Yes'))
        fp = np.sum((np.array(output) == 'Yes') == (np.array(target) == 'No'))
        fn = np.sum((np.array(output) == 'No') == (np.array(target) == 'Yes'))
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        return 0 if precision + recall == 0 else (2 * precision * recall) / (precision + recall)
    
    def __init__(self):
        super().__init__()

        self.t_scores = []
        self.t_losses = []
        self.v_scores = []
        self.v_losses = []

        self.stats_mem = []

    def train(self, source, target):
        outputs = list(super().train(source, target))
        self.t_losses.append(np.average([o['loss'] for o in outputs]))
        self.t_scores.append(self.__f1score([o['predicted_label'] for o in outputs], target))
        return outputs

    def test(self, source, target):
        outputs = list(super().train(source, target))
        self.v_losses.append(np.average([o['loss'] for o in outputs]))
        self.v_scores.append(self.__f1score([o['predicted_label'] for o in outputs], target))
        return outputs

    def predict(self, sample):
        return list(super().predict(sample))

    def stats(self):
        stats = {
            't_loss': np.average(self.t_losses) if self.t_losses else 0,
            'v_loss':  np.average(self.v_losses) if self.v_losses else 0,
            't_accuracy': np.average(self.t_scores) if self.t_scores else 0,
            'v_accuracy': np.average(self.v_scores) if self.v_scores else 0,
        }

        self.stats_mem.append(stats)

        self.t_losses = []
        self.t_scores = []
        self.v_losses = []
        self.v_scores = []

        return stats
