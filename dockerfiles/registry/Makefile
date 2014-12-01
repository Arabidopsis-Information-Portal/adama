.PHONY: clean

build: Dockerfile fig.yml handler/* registry.conf ../serfnode/build
	fig build
	touch build

clean:
	rm build

