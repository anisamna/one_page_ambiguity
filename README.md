# Ambiguity

## Installation

## File Media

- Buat folder media:
    - /media/file/treeps
    - /media/file/treeimage


### Database

```sql
CREATE DATABASE ambiguity_db;
CREATE USER ambiguity_user WITH PASSWORD 'NUy7UmJAH7xF3srqBoGGyyP5cJ1n3r';
ALTER ROLE ambiguity_user SET client_encoding TO 'utf8';
ALTER ROLE ambiguity_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ambiguity_user WITH PASSWORD 'NUy7UmJAH7xF3srqBoGGyyP5cJ1n3r';
GRANT ALL PRIVILEGES ON DATABASE ambiguity_db TO ambiguity_user;
```

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

https://pythonguides.com/convert-html-page-to-pdf-using-django/#:~:text=Django%20HTML%20to%20PDF%20example,-Firstly%2C%20you%20have&text=In%20the%20view%20class%2C%20we,in%20the%20process.py%20file.&text=In%20this%20urls.py%20file,py%20file%20will%20be%20called.