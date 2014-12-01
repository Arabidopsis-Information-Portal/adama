.PHONY: clean

build: Dockerfile fig.yml handler/* zookeeper.conf zoo.cfg ../serfnode/build
	fig build
	touch build

clean:
	rm build

