.PHONY: clean

build: Dockerfile fig.yml handler/* rabbitmq.conf ../serfnode/build
	fig build
	touch build

clean:
	rm build

