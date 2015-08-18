# Build 'common' image for all containers

.PHONY: clean

build: Dockerfile
	$(DOCKER) build --no-cache=$(NO_CACHE) -t adama/common_base .
	touch build
	touch .

clean:
	rm build
