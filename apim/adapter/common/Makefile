# Build 'common' image for all containers

.PHONY: clean

build: Dockerfile
	docker build --no-cache=$(NO_CACHE) -t common .
	touch build
	touch .

clean:
	rm build
