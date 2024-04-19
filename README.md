# Ambiguity

[![PyPI version](https://badge.fury.io/py/Django.svg)](https://badge.fury.io/py/Django)

## File Media

- create media directory:

  - /media/file/treeps
  - /media/file/treeimage

## Installation

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

do in terminal, type python, copy code in shell:

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
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,ner,parse,depparse -status_port 9000 -port 9000 -timeout 15000 
```

### Clear Cache SentenceTransformer

```python
import gc
import torch

gc.collect()
torch.cuda.empty_cache()
# https://github.com/UKPLab/sentence-transformers/issues/487
```

### Install with Docker

> Install docker and docker compose in this [link](https://docs.docker.com/engine/install/ubuntu/)

- Docker dev

    ```sh
    docker compose -f docker-compose.dev.yaml up -d
    ```

- Docker prod

    ```sh
    docker compose up -d
    ```

## Documentation

- [NLTK](https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK)
- [template](https://bootstrapmade.com/demo/NiceAdmin/)
