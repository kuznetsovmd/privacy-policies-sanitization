

def natasha(input_docs, names_dataset):

    from natasha import (
    Segmenter,
    MorphVocab,  
    PER,
    NamesExtractor,
    NewsNERTagger,   
    NewsEmbedding,
    Doc
)
 
    emb = NewsEmbedding()
    segmenter = Segmenter()
    morph_vocab = MorphVocab()
    ner_tagger = NewsNERTagger(emb)
    names_extractor = NamesExtractor(morph_vocab)
    

    for f in list_files(input_docs):
        doc = Doc(read_lines(f))
        doc.segment(segmenter)
        doc.tag_ner(ner_tagger)
        
        for span in doc.spans:
            span.normalize(morph_vocab)

        {_.text: _.normal for _ in doc.spans}
        
        for span in doc.spans:
            if span.type == PER:
                span.extract_fact(names_extractor)
        
        {_.normal: _.fact.as_dict for _ in doc.spans if _.fact}
        
        # doc.ner.print()