FROM python

WORKDIR ~/monitoring

COPY receiver.py

VOLUME /recordings

ENTRYPOINT ["receiver.py"]

CMD ["/recordings/"]
