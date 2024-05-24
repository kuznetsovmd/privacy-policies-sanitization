### What else to do
1. ~~Sanitization~~
    1. ~~Rebuild~~
    1. ~~Filter statistics~~
    1. ~~Structure statistics~~
    1. ~~Frequent words~~
2. NE Removal
    1. ~~Natasha~~ 51m 33s
    3. ~~Spacy~~ 9m 44s
    2. ~~Stanza~~ 10h 19m 50s
    4. ~~Transformers~~ 5h 10m 5s
    4. ~~DeepPavlov~~ 25m 30s
    5. Regexes
        - ~~Persons~~
            - ~~Parse datasets~~
            - ~~Make regexes~~
            - Extend prefix words
        - Addresses
            - ~~Parse PHIAS~~
            - Make regexes
    6. ~~Endings removal (nltk sbow stemmer)~~
    7. Gather statistics
    8. Make dictionary from all found NEs
    9. Remove

### Installation
```
$ activate
$ pip install -r requirements.txt
$ pip install torch --index-url https://download.pytorch.org/whl/rocm6.0
```

### Run
```
$ activate
$ HSA_OVERRIDE_GFX_VERSION=10.3.0 python main.py cmd [flags]
```

### Supplementary docs
* [Transformers]()
* [DeepPavlov](https://docs.deeppavlov.ai/en/master/features/models/NER.html#2.-Get-started-with-the-model)
* [Natasha]()
* [Stanza]()
* [Spacy]()
* [PyTorch]()