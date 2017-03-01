FROM reg.weizom.com/wzbase/python27:1.0

RUN pip install -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com -U \
  uwsgi \
  upyun \
  && rm -rf ~/.pip

EXPOSE 8001
ADD ./dist /service
WORKDIR /service

RUN pip install -U \
    git+https://git2.weizzz.com:84/microservice/eaglet.git \
    git+https://git2.weizzz.com:84/microservice/mns_python_sdk.git \
    git+https://git2.weizzz.com:84/microservice/servicecli.git \
  && rm -rf ~/.pip ~/.cache

ENTRYPOINT ["/usr/local/bin/dumb-init", "/bin/bash", "start_service.sh"]
