FROM python:3.8-slim-buster

RUN adduser --system --no-create-home --group docker

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

USER docker

CMD [ "python3", "-m" , "flask", "-e", "env_file", "run", "--host=0.0.0.0" ]
