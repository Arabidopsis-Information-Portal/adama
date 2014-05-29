# Build 'common' image for all containers

.PHONY: clean

build: Dockerfile
	docker build -t common .
	touch build
	touch .

clean:
	rm build
