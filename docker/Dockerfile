FROM cr.yandex/crps9i3eull3qc5u9m17/cbot-python-builder:latest as cbot-trunk-info-producer-mts-builder

RUN mkdir -p /install/data
RUN apt-get update && apt-get install -y --no-install-recommends build-essential pipenv
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt && \
    pip install --ignore-installed --prefix=/install -r /tmp/requirements.txt


FROM cr.yandex/crps9i3eull3qc5u9m17/cbot-python:latest as cbot-trunk-info-producer-mts
COPY --from=cbot-trunk-info-producer-mts-builder /install /usr/local
COPY . /app
WORKDIR /app

CMD [ "$@" ]
