FROM python:3.9.18-slim
COPY . /ambiguity

WORKDIR /ambiguity
ENV PYTHONUNBUFFERED=1
RUN apt update -y
# RUN apt upgrade
RUN apt install gcc postgresql-client -y 
RUN pip install --upgrade pip
RUN pip install -r requirements_prod.txt
RUN python -m spacy download en_core_web_sm

RUN chmod +x wait-for-postgres.sh
EXPOSE 8000
