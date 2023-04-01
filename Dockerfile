# Define image to use
FROM python:3.8.2-alpine

#define workdir
WORKDIR /app

# Copy requirements for installation
COPY ./requirements.txt ./

# Install dependencies
RUN /usr/local/bin/python -m pip install --upgrade pip 
RUN pip install psycopg2-binary
RUN pip install -r requirements.txt

RUN mkdir event_service
COPY ./event_service/ ./event_service

# Define volume to sync changes automatically
VOLUME /event_service

EXPOSE 8000

# Run app
ENTRYPOINT uvicorn event_service.main:app --host 0.0.0.0 --reload
