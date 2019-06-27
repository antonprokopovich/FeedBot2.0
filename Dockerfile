FROM python:3.6

COPY . /app

WORKDIR /app

RUN pip install pipenv
COPY Pipfile /app/
COPY Pipfile.lock /app/
RUN pipenv install --deploy --system
