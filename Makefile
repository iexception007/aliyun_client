REPO=iexception007/aliyun_client
VERSION=v0.0.1

.PHONY: build run clear logs
build:
	docker build -t ${REPO}:${VERSION} .

run: clear
	docker run -it --rm --name aliyun_client ${REPO}:${VERSION}

run_start:
	docker run -it --rm --name aliyun_client ${REPO}:${VERSION} sh -c "python /code/aliyun_client.py --start"

run_stop:
	docker run -it --rm --name aliyun_client ${REPO}:${VERSION} sh -c "python /code/aliyun_client.py --stop"

run_reset:
	docker run -it --rm --name aliyun_client ${REPO}:${VERSION} sh -c "python /code/aliyun_client.py --reset"


clear:
	-docker rm -f aliyun_client

logs:
	docker logs -f aliyun_client
