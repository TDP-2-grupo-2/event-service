FROM python:3.8.2-alpine

WORKDIR /app

COPY ./requirements.txt ./

RUN /usr/local/bin/python -m pip install --upgrade pip 
RUN pip install psycopg2-binary

RUN pip install -r requirements.txt

RUN mkdir event_service

COPY ./event_service/ ./event_service

#VOLUME ./event_service /event_service

EXPOSE 8000

ENTRYPOINT uvicorn event_service.main:app --host 0.0.0.0 --reload