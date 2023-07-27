# Ambiguity

## Installation

## File Media

- Buat folder media:
    - /media/file/treeps
    - /media/file/treeimage
 
### Download Resource NLTK

lakukan di terminal, ketik python, copy code di shell:

```python
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
```

### Running Service NLTK

```sh
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer \
-preload tokenize,ssplit,pos,lemma,ner,parse,depparse \
-status_port 9000 -port 9000 -timeout 15000 & 
```

di laptop Anis berubah jadi spt ini:
```sh
Start-Process java -ArgumentList '-mx4g', '-cp', '*', 'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-preload', 'tokenize,ssplit,pos,lemma,ner,parse,depparse', '-port', '9000', '-timeout', '15000'
```

## Documentation

- [NLTK](https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK)
- [template](https://bootstrapmade.com/demo/NiceAdmin/)
