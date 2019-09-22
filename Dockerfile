FROM python:3

ADD . /

RUN pip install -r requirements.txt

ENV PYTHONPATH="$PYTHONPATH:${PWD}"

CMD ["python", "api/app.py"]

