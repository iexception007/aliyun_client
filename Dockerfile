FROM python:2.7-alpine
MAINTAINER zhouyi 6098550@qq.com

RUN mkdir -p /code && mkdir -p /root/.pip
COPY source/pip.conf      /root/.pip/
COPY source/repositories  /etc/apk/

RUN apk update \
 && apk add --no-cache curl gcc g++ jq

RUN pip install pyyaml \
 && pip install aliyun-python-sdk-core \
 && pip install aliyun-python-sdk-ecs

COPY aliyun_client.py /code
COPY config.yml       /code
WORKDIR /code
CMD python aliyun_client.py
#CMD python aliyun_client.py | jq -r '.Instances.Instance[] | "ID:" + .InstanceId + " IP:" + .VpcAttributes.PrivateIpAddress.IpAddress[]'