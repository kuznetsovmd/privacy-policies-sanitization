

class ParagraphsDataset():
    def __init__(self, sources, targets):
        assert len(sources) == len(targets), 'outputs & targets are not equal on length'
        self.samples = list(zip(sources, targets))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]
    