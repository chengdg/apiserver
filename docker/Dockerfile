FROM reg.weizom.com/wzbase/python27:1.0

RUN pip install -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com -U \
  uwsgi \
  upyun \
  && rm -rf ~/.pip

EXPOSE 8001
ADD ./dist /service
WORKDIR /service

ENTRYPOINT ["/usr/local/bin/dumb-init", "/bin/bash", "start_service.sh"]
