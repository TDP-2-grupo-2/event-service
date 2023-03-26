FROM python:3.8.2-alpine

WORKDIR /app

COPY ./requirements.txt ./

RUN /usr/local/bin/python -m pip install --upgrade pip 
RUN pip install -r requirements.txt

WORKDIR /event-service

VOLUME . /event-service

EXPOSE 8000

CMD ["uvicorn", "main:app --reload"]