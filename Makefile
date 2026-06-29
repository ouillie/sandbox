.PHONY: install proxy

proxy:
	podman build ./proxy --tag=sandbox-proxy:latest

install:
	install -m755 ./sandbox /usr/local/bin/sandbox
