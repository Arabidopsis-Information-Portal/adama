# Build 'python' image to run Python apps

.PHONY: clean

build: Dockerfile ../common *.py
	cp ../../tasks.py .
	$(DOCKER) build --no-cache=$(NO_CACHE) -t python .
	rm -rf tasks.py
	touch build
	touch .

clean:
	rm build
