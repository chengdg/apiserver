# reg.weizzz.com:5000/wz/weapp-apiserver:1.0
FROM reg.weizzz.com:5000/wz/python27:1.0
MAINTAINER victor "gaoliqi@weizoom.com"

RUN pip install -U \
  uwsgi \
  upyun \
  && rm -rf ~/.pip

COPY . /apiserver/

VOLUME ["/apiserver"]

WORKDIR /apiserver

EXPOSE 8001

#CMD ["/bin/bash", "/weapp/api/start.sh"]
ENTRYPOINT ["/usr/local/bin/dumb-init", "/bin/bash", "start.sh"]
