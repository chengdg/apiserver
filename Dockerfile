# reg.weizzz.com:5000/wz/weapp-apiserver:1.0
FROM python:2.7
MAINTAINER victor "gaoliqi@weizoom.com"

# install gcc for pycrypto
RUN apt-get update \
  && apt-get install -y gcc libmysqlclient-dev mysql-client libjpeg-dev gfortran libsqlite3-dev

RUN pip install -U \
  Cython \
  falcon \
  "peewee<2.7" \
  "pymongo==2.5" \
  beautifulsoup4 \
  redis \
  PyMySQL \
  celery \
  pycrypto \
  pysqlite \
  "Django<1.7" \
  poster \
  Pillow \
  requests \
  beautifulsoup \
  upyun

# to support BDD
RUN pip install behave factory_boy selenium \
  && rm -rf ~/.pip

COPY * /weapp/api

CMD ["/bin/bash", "/weapp/api/start.sh"]
