.PHONY: clean

build: Dockerfile fig.yml handler/* zookeeper.conf zoo.cfg
	fig build
	touch build

clean:
	rm build

