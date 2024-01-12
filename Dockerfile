FROM python:3.11.6

COPY requirements.txt /usr/src/app/

RUN pip3 install -r /usr/src/app/requirements.txt

WORKDIR /usr/src/app

COPY . .

WORKDIR ./nightary

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

EXPOSE 8000
