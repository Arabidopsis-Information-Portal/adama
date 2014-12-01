.PHONY: clean

build: Dockerfile handler/* serfnode.conf
	docker build -t serfnode .
	touch build

clean:
	rm build
