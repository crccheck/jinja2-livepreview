FROM python:3.5-alpine
MAINTAINER Chris Chang

RUN apk add --no-cache \
      # Ansible/pycypto
      gcc g++ make libffi-dev openssl-dev

COPY requirements.txt /app/requirements.txt
RUN pip install --disable-pip-version-check -r /app/requirements.txt

# It's impossible to install node here to build static files, so we'll have
# to rely on it existing on the host and getting copied in. When node can be
# compiled on a Python 3 host, we can install node.
COPY . /app
WORKDIR /app

ENV PORT 8080
EXPOSE 8080

CMD ["python", "web.py"]
