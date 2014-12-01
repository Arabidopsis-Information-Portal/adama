.PHONY: clean

build: Dockerfile fig.yml handler/* worker.conf ../serfnode/build
	fig build
	touch build

clean:
	rm build

