# Build 'javascript' image to run node apps

.PHONY: clean

build: Dockerfile ../common *.js
	docker build -t javascript .
	touch build
	touch .

clean:
	rm build
