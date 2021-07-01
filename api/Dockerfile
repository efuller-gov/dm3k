FROM python:3.7.2
WORKDIR /app
ADD . /app
WORKDIR ../examples
ADD ../examples /examples
WORKDIR ../optimizer
ADD ../optimizer /optimizer
WORKDIR ../tests
ADD ../tests /tests
RUN pip install -r requirements.txt
CMD [ "uwsgi", "app.ini" ]