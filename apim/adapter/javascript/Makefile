# Build 'javascript' image to run node apps

.PHONY: clean

build: Dockerfile ../common *.js
	docker build --no-cache=$(NO_CACHE) -t javascript .
	touch build
	touch .

clean:
	rm build
