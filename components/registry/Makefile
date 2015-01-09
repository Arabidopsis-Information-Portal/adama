.PHONY: clean

build: Dockerfile fig.yml handler/* registry.conf
	fig build
	touch build

clean:
	rm build

