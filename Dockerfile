FROM python:3.7-alpine

RUN apk update && apk add gcc linux-headers musl-dev libxml2-dev libxslt-dev

WORKDIR /usr/src/app

COPY Pipfile* .

RUN pip install pipenv && set -ex && pipenv install --system --deploy

COPY . .

CMD ["python3", "-m", "trunk_producer_mts"]
