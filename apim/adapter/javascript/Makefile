# Build 'javascript' image to run node apps

.PHONY: clean

build: Dockerfile ../common *.js
	$(DOCKER) build --no-cache=$(NO_CACHE) -t javascript .
	touch build
	touch .

clean:
	rm build
