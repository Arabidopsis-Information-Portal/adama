# Build 'python' image to run Python apps

.PHONY: clean

build: Dockerfile ../common *.py
	cp ../../tasks.py .
	cp ../../store.py .
	$(DOCKER) build --no-cache=$(NO_CACHE) -t adama/python_base .
	rm -rf tasks.py store.py
	touch build
	touch .

clean:
	rm build
