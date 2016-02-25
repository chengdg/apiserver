# reg.weizzz.com:5000/wz/weapp-apiserver:1.0
FROM reg.weizzz.com:5000/wz/python27:1.0
MAINTAINER victor "gaoliqi@weizoom.com"

RUN pip install -U \
  falcon \
  "peewee<2.7" \
  && rm -rf ~/.pip

COPY . /weapp/api/

VOLUME ["/weapp/api"]

WORKDIR /weapp/api

#CMD ["/bin/bash", "/weapp/api/start.sh"]
ENTRYPOINT ["/usr/local/bin/dumb-init", "/bin/bash", "start.sh"]
