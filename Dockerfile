# reg.weizzz.com:5000/wz/weapp-apiserver:1.0
FROM reg.weizzz.com:5000/wz/python27
MAINTAINER victor "gaoliqi@weizoom.com"

# install gcc for pycrypto
RUN apt-get update \
  && apt-get install -y gcc libmysqlclient-dev mysql-client libjpeg-dev gfortran libsqlite3-dev

RUN pip install -U \
  falcon \
  "peewee<2.7" \
  && rm -rf ~/.pip

COPY . /weapp/api/

CMD ["/bin/bash", "/weapp/api/start.sh"]
