import shutil
import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F


class NAN(Exception):
    pass


class BaseModel:

    def train2(self, label_tensor, sample_tensor):
        self.module.train()
        o = []
        l = []
        self.module.init_hidden()
        self.optimizer.zero_grad()
        for i in range(sample_tensor.size()[0]):
            o.append(self.module(sample_tensor[i]))
            loss = self.criterion(o[-1], label_tensor[i])
            if loss.isnan(): 
                raise NAN('Loss is nan!')
            l.append(loss.item())
            loss.backward(retain_graph=True)
            self.optimizer.step()
        return o, l

    def test2(self, label_tensor, sample_tensor):
        self.module.eval()
        o = []
        l = []
        with torch.no_grad():
            self.module.init_hidden()
            for i in range(sample_tensor.size()[0]):
                o.append(self.module(sample_tensor[i]))
                l.append(self.criterion(o[-1], label_tensor[i]).item())
            return o, l

    def predict2(self, sample_tensor):
        self.module.eval()
        o = []
        with torch.no_grad():
            self.module.init_hidden()
            for i in range(sample_tensor.size()[0]):
                o.append(self.module(sample_tensor[i]))
            return o

    def train(self, label_tensor, sample_tensor):
        self.module.train()
        for i in range(sample_tensor.size()[0]):
            output = self.module(sample_tensor[i])
        loss = self.criterion(output, label_tensor)
        if loss.isnan(): 
            raise NAN('Loss is nan!')
        loss.backward()
        self.optimizer.step()
        return output, loss.item()

    def test(self, label_tensor, sample_tensor):
        self.module.eval()
        with torch.no_grad():
            self.module.init_hidden()
            for i in range(sample_tensor.size()[0]):
                output = self.module(sample_tensor[i])
            loss = self.criterion(output, label_tensor)
            return output, loss.item()

    def predict(self, sample_tensor):
        self.module.eval()
        with torch.no_grad():
            self.module.init_hidden()
            for i in range(sample_tensor.size()[0]):
                output = self.module(sample_tensor[i])
            return output


class Model(BaseModel):
    
    @staticmethod
    def __check(output, label):
        _, top_i = output.topk(1)
        return top_i.item() == label.item()
    
    def __init__(self):
        super().__init__()
        self.last_epoch = 0
        self.train_iters = 0
        self.validation_iters = 0
        self.train_loss = 0
        self.validation_loss = 0
        self.train_accuracy = []
        self.validation_accuracy = []
        self.train_losses = []
        self.validation_losses = []
        self.train_accuracies = []
        self.validation_accuracies = []

    def train2(self, label_tensor, sample_tensor):
        output, loss = super().train2(label_tensor, sample_tensor)
        a = [self.__check(output[i], label_tensor[i]) for i in range(label_tensor.size()[0])]
        self.train_accuracy.append(sum(a) / len(a))
        self.train_loss += sum(loss) / len(loss)
        self.train_iters += 1
        return output, loss

    def test2(self, label_tensor, sample_tensor):
        output, loss = super().test2(label_tensor, sample_tensor)
        a = None
        try:
            a = [self.__check(output[i], label_tensor[i]) for i in range(label_tensor.size()[0])]
        except IndexError:
            print(f': {len(output)=}, {len(label_tensor)=}')

        self.validation_accuracy.append(sum(a) / len(a))
        self.validation_loss += sum(loss) / len(loss)
        self.validation_iters += 1
        return output, loss

    def train(self, label_tensor, sample_tensor):
        output, loss = super().train(label_tensor, sample_tensor)
        self.train_accuracy.append(self.__check(output, label_tensor))
        self.train_loss += loss
        self.train_iters += 1
        return output, loss

    def test(self, label_tensor, sample_tensor):
        output, loss = super().test(label_tensor, sample_tensor)
        self.validation_accuracy.append(self.__check(output, label_tensor))
        self.validation_loss += loss
        self.validation_iters += 1
        return output, loss

    def predict(self, sample_tensor):
        return super().predict(sample_tensor)
        
    def epoch(self):
        self.train_losses.append(self.train_loss / self.train_iters)
        self.validation_losses.append(self.validation_loss / self.validation_iters)
        self.train_accuracies.append(sum(self.train_accuracy) / len(self.train_accuracy))
        self.validation_accuracies.append(sum(self.validation_accuracy) / len(self.validation_accuracy))

        self.train_iters = 0
        self.validation_iters = 0

        self.train_loss = 0
        self.validation_loss = 0
        self.train_accuracy = []
        self.validation_accuracy = []

        self.last_epoch += 1


def build_model(*args, **kwargs):
    model = Model()
    model.module = kwargs['module'](**kwargs['module_parameters'])
    model.optimizer = kwargs['optimizer'](model.module.parameters(), **kwargs['optimizer_parameters'])
    model.criterion = kwargs['criterion'](**kwargs['criterion_parameters'])
    model.path = kwargs['path']

    if kwargs['pretrained']:
        loaded = torch.load(f'{kwargs["path"]}.pt')

        if loaded:
            model.module.load_state_dict(loaded['model_state_dict'])
            model.optimizer.load_state_dict(loaded['optimizer_state_dict'])
            model.last_epoch = loaded['last_epoch']
            model.train_losses = loaded['train_losses']
            model.validation_losses = loaded['validation_losses']
            model.train_accuracies = loaded['train_accuracies']
            model.validation_accuracies = loaded['validation_accuracies']

    else:
        shutil.rmtree(os.path.dirname(model.path), ignore_errors=True)

    return model


def save_model(model, version=''):
    version = f'_{version}' if version else ''
    os.makedirs(os.path.dirname(model.path), exist_ok=True)
    torch.save({
        'last_epoch': model.last_epoch,
        'model_state_dict': model.module.state_dict(),
        'optimizer_state_dict': model.optimizer.state_dict(),
        'train_losses': model.train_losses,
        'validation_losses': model.validation_losses,
        'train_accuracies': model.train_accuracies,
        'validation_accuracies': model.validation_accuracies,
    }, f'{model.path}{version}.pt')


class RNN_2xR1(nn.Module):
    def __init__(self, input_size=64, hidden_size=64, output_size=64, dropout=0.1, device='cpu'):
        super(RNN_2xR1, self).__init__()
        self.device = device
        self.hidden_size = hidden_size

        self.fc1 = nn.Linear(input_size + hidden_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size + hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(dropout)
        
        torch.nn.init.xavier_uniform_(self.fc1.weight)
        torch.nn.init.xavier_uniform_(self.fc2.weight)
        torch.nn.init.xavier_uniform_(self.fc3.weight)

        self.to(self.device)
        self.init_hidden()

    def forward(self, input):
        input -= input.min()
        input /= input.max()

        self.hidden1 = F.relu(self.fc1(torch.cat((input, self.hidden1), 1)))
        self.hidden1 = self.dropout(self.hidden1)

        self.hidden2 = F.relu(self.fc2(torch.cat((self.hidden1, self.hidden2), 1)))
        self.hidden2 = self.dropout(self.hidden2)

        return self.fc3(self.hidden2)

    def init_hidden(self):
        self.hidden1 = torch.zeros(1, self.hidden_size, device=self.device)
        self.hidden2 = torch.zeros(1, self.hidden_size, device=self.device)


class LSTM(nn.Module):
    def __init__(self, input_size=64, hidden_size=64, output_size=64, device='cpu', **kwargs):
        super(LSTM, self).__init__()
        self.device = device
        self.hidden_size = hidden_size

        self.lstm = nn.LSTM(input_size, hidden_size, 2)
        self.fc = nn.Linear(hidden_size, output_size)

        self.to(self.device)

    def forward(self, input):
        input -= input.min()
        input /= input.max()

        output, _ = self.lstm(input)
        output = self.fc(output)
        return output

    def init_hidden(self):
        pass
