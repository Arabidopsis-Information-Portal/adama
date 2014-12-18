.PHONY: clean

build: Dockerfile fig.yml handler/* rabbitmq.conf
	fig build
	touch build

clean:
	rm build

