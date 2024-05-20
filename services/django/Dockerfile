FROM python:3.5-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  libffi-dev libldap2-dev libsasl2-dev libcairo2 libpangocairo-1.0-0 \
  # && apt-get install ack-grep adminer aptitude binutils elasticsearch gdal-bin git git-core libcairo2 libffi-dev libgdal-dev libgdk-pixbuf2.0-0 libjpeg-dev libldap2-dev libpango-1.0-0 libpangocairo-1.0-0 libproj-dev libsasl2-dev libssl-dev libxml2-dev libxslt-dev nfs-common open-vm-tools openjdk-8-jre postgis postgresql postgresql-client postgresql-server-dev-all python3-cffi python3-dev python3-gdal python3-pip python3-psycopg2 python3-setuptools python3-venv shared-mime-info vim-nox zsh
  # psycopg2 dependencies
  libpq-dev \
  # gdal libraries
  binutils libproj-dev gdal-bin \
  # ldap dependencies
  libldap2-dev libsasl2-dev ldap-utils \
  # lxml depedndencies
  # && apt-get install -y libxml2-dev libxslt-dev python-dev \
  # && apt-get install -y python3-lxml \
  libgdk-pixbuf2.0-0 libjpeg-dev \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY ../volumes/django/requirements.txt /requirements/
# COPY ../volumes/django/requirements-dev.txt /requirements/
RUN pip install -U pip \
  && pip install -r /requirements/requirements.txt
# && pip install -r /requirements/requirements-dev.txt

COPY ../services/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

WORKDIR /app

ENTRYPOINT ["/entrypoint"]