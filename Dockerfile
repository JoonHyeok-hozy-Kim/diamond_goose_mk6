FROM python:3.9.0

WORKDIR /home/

RUN git clone https://github.com/JoonHyeok-hozy-Kim/diamond_goose_mk6.git

WORKDIR /home/diamond_goose_mk6/

RUN pip install -r requirements.txt

RUN echo "SECRET_KEY=django-insecure-q%d=zmb+8%ai@to5er!75!#zg+%s7o=a)c^vck_bq1$yx))k9u" > .env

RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]