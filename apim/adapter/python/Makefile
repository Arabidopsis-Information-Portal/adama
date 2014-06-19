# Build 'python' image to run Python apps

.PHONY: clean

build: Dockerfile ../common *.py
	$(DOCKER) build --no-cache=$(NO_CACHE) -t python .
	touch build
	touch .

clean:
	rm build
