import torch


class NAN(Exception):
    pass


class BaseSanitizationModel:

    def train(self, label_tensor, sample_tensor):
        self.module.train()
        o = []
        l = []
        self.module.init_hidden()
        for i in range(sample_tensor.size()[0]):
            o.append(self.module(sample_tensor[i]))
            loss = self.criterion(o[-1], label_tensor[i])
            if loss.isnan(): 
                raise NAN('Loss is nan!')
            l.append(loss)
        sum(l).backward(retain_graph=True)
        self.optimizer.step()
        self.optimizer.zero_grad()
        return o, l

    def test(self, label_tensor, sample_tensor):
        self.module.eval()
        self.module.init_hidden()
        o = []
        l = []
        with torch.no_grad():
            for i in range(sample_tensor.size()[0]):
                o.append(self.module(sample_tensor[i]))
                l.append(self.criterion(o[-1], label_tensor[i]))
            return o, l

    def predict(self, sample_tensor):
        self.module.eval()
        self.module.init_hidden()
        o = []
        with torch.no_grad():
            for i in range(sample_tensor.size()[0]):
                o.append(self.module(sample_tensor[i]))
            return o


class SanitizationModel(BaseSanitizationModel):
    
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

    def train(self, label_tensor, sample_tensor):
        output, loss = super().train(label_tensor, sample_tensor)
        a = [self.__check(output[i], label_tensor[i]) for i in range(label_tensor.size()[0])]
        self.train_accuracy.append(sum(a) / len(a))
        self.train_loss += sum(loss) / len(loss)
        self.train_iters += 1
        return output, loss

    def test(self, label_tensor, sample_tensor):
        output, loss = super().test(label_tensor, sample_tensor)
        a = None
        try:
            a = [self.__check(output[i], label_tensor[i]) for i in range(label_tensor.size()[0])]
        except IndexError:
            print(f': {len(output)=}, {len(label_tensor)=}')

        self.validation_accuracy.append(sum(a) / len(a))
        self.validation_loss += sum(loss) / len(loss)
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
