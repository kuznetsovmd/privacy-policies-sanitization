### What else to do
1. ~~Do sanitization experiments~~
    1. ~~Custom models~~
    1. ~~Bert~~
1. Do ner remove
    1. Custom remover
        - Normalize, test
        - PHIAS
        - Cyrillic names
    1. DeepPavlov
    1. SpaCy
    1. Natasha

### Installation
```
$ activate
$ pip install -r requirements.txt
$ pip install torch --index-url https://download.pytorch.org/whl/rocm5.7
```

### Run
```
$ activate
$ HSA_OVERRIDE_GFX_VERSION=10.3.0 python main.py cmd [flags]
```

### Supplementary docs
* [PyTorch]()
* [Bert]()
* [Transformers]()
* [DeepPavlov](https://docs.deeppavlov.ai/en/master/features/models/NER.html#2.-Get-started-with-the-model)
* [Natasha]()
* [Spacy]()