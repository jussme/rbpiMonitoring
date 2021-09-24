FROM python:3

ENV WORK_DIR=/monitoring

WORKDIR $WORK_DIR

COPY receiver.py ./

COPY quickstart.py ./

RUN ["mkdir", "recordings"]

RUN ["pip", "install", "--upgrade", "google-api-python-client", "google-auth-httplib2", "google-auth-oauthlib"]

ENTRYPOINT ["python3","./receiver.py"]

CMD ["recordings","60000","True"]
