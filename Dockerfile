FROM python:3.6-alpine
MAINTAINER Chris Chang

RUN apk add --no-cache \
      # Ansible/pycrypto
      gcc g++ make libffi-dev openssl-dev

COPY requirements.txt /app/requirements.txt
RUN pip install --disable-pip-version-check -r /app/requirements.txt

COPY . /app
WORKDIR /app

ENV PORT 8080
EXPOSE 8080

CMD ["python", "web.py"]
