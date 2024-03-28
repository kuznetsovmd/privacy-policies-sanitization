import torch
import torch.nn as nn
import torch.nn.functional as F


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
