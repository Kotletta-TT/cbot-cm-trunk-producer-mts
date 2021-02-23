FROM python:3.9

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir pipenv && pipenv install --system --deploy --clear

CMD ["python", "main.py"]