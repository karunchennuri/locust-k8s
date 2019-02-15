ARG PYTHON_VERSION=3.7.1
FROM python:${PYTHON_VERSION}-alpine as pydeps
COPY requirements.txt /
COPY docker-entry.sh /

RUN apk --no-cache add --virtual=.build-dep build-base \
    && apk --no-cache add libzmq \
    && apk --no-cache add libffi-dev \
    && apk --no-cache add openssl-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-dep

RUN chmod +x /docker-entry.sh

ENTRYPOINT ["/docker-entry.sh"]
EXPOSE 8089 5557 5558

