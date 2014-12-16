.PHONY: clean

build: Dockerfile fig.yml handler/* *.conf ../serfnode/build
	fig build
	touch build

clean:
	rm build

