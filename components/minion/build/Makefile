.PHONY: clean

build: Dockerfile handler/* *.conf
	docker build -t minion .
	touch .build

clean:
	rm .build

