FROM python:3.8

WORKDIR /work

COPY ./requirements.txt /work/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /work/requirements.txt

COPY . /work

CMD ["python", "app.py"]